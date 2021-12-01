# Sprite classes for game
from os import write
import pygame as pg
import random as rand
import math
import time
import Settings as s
from Display import collide_hit_rect
vec = pg.math.Vector2


def roach_special(player, count):
    if count == 30:
        for i in range(-20, 21, 10):
            target = player.pos + vec(20, i)
            if player.direction == 'Left':
                target = player.pos + vec(-20, i)
            damage = s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE']
            Projectile(player.game, player.pos.x, player.pos.y, 'Roach', 150, target, 0.5, 0, 200, damage, True, 200, True, 4)
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


def bombardier_special(player, count):
    if count == 30:
        for enemy in player.game.enemies:
            if player.pos.distance_squared_to(enemy.pos) < 96**2:
                enemy.hit(s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE'])
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


def ant_special(player, count):
    if count == 30:
        for enemy in player.game.enemies:
            if player.pos.distance_squared_to(enemy.pos) < 960**2:
                Projectile(player.game, player.pos.x + 100, player.pos.y, 'Ant', 150, enemy.pos, 0.5, 0, 1000,
                           s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE'], True, 200, True, 4)
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


def hercules_special(player, count):
    player.acc.x = 0.6
    if player.direction == 'Left':
        player.acc.x = -0.6
    hits = pg.sprite.spritecollide(player, player.game.enemies, False, collide_hit_rect)
    for hit in hits:
        hit.hit(s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE'])
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


def wasp_special(player, count):
    if count == 30:
        target = vec(player.pos.x + 144, player.pos.y)
        if player.direction == 'Left':
            target = vec(player.pos.x - 144, player.pos.y)
        Projectile(player.game, player.pos.x, player.pos.y, 'Wasp', 150, target, 0.1, 0, 5000,
                   s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE'], True, 200, True, 10)
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


special_attacks = {
    'Roach': roach_special,
    'Bombardier': bombardier_special,
    'Ant': ant_special,
    'Hercules': hercules_special,
    'Wasp': wasp_special
}


def collide_with_walls(sprite, group, dir, solid=True):
    collided = False
    if dir == 'x':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            for hit in hits:
                if hit != sprite:
                    collided = hit
                    if hit.rect.centerx > sprite.hit_rect.centerx:
                        sprite.pos.x = hit.rect.left - (sprite.hit_rect.width / 2) - 1
                    if hit.rect.centerx < sprite.hit_rect.centerx:
                        sprite.pos.x = hit.rect.right + (sprite.hit_rect.width / 2) + 1
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            for hit in hits:
                if hit != sprite:
                    if solid:
                        collided = hit
                        if hit.rect.centery > sprite.hit_rect.centery:
                            sprite.pos.y = hit.rect.top - (sprite.hit_rect.height / 2) - 1
                        if hit.rect.centery < sprite.hit_rect.centery:
                            collided = False
                            sprite.acc.y = 0
                            sprite.vel.y = 0
                            sprite.pos.y = hit.rect.bottom + \
                                (sprite.hit_rect.height / 2) + 1
                    elif sprite.hit_rect.bottom <= hit.rect.top + 20:
                        collided = hit
                        sprite.pos.y = hit.rect.top - (sprite.hit_rect.height / 2) - 1

            sprite.hit_rect.centery = sprite.pos.y
    return collided


def play_sound(game, name):
    snd = game.get_sound(name + '.mp3')
    snd.play()


def write_text(game, text, size, color, pos):
    font = pg.font.Font(game.font, size)
    surf = font.render(text, True, color)
    game.screen.blit(surf, pos)


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.current_bug = 'Parasite'
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.attack_type = s.Animation.FRONT_A
        self.animation_type = s.Animation.IDLE
        self.direction = s.Animation.IDLE
        self.animation_phase = 0
        self.image = self.game.all_images[self.current_bug][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = pg.Rect.copy(s.BUGS[self.current_bug]['HIT_RECT'])
        self.hit_rect.center = self.rect.center
        self.jump = False
        self.jump_leniency = -1
        self.in_air = False
        self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
        self.stamina = self.max_stamina
        self.max_health = s.HEALTH
        self.health = self.max_health
        self.next_animation_tick = 0
        self.parasite_cooldown = 0
        self.attacking = 0
        self.attack_leniency = -1
        self.special = -1
        self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
        self.platform = Obstacle(self.game, 0, 0, 0, 0)
        self.checkpoint = None

    def handle_events(self, event=pg.event.Event):
        # Only update variables if key pressed
        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            # Update direction
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                self.animation_type = s.Animation.IDLE
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                self.animation_type = s.Animation.IDLE
            if event.key == pg.K_k:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.FRONT_A
            if event.key == pg.K_j:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.UP_A
            if event.key == pg.K_l:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.DOWN_A
            if event.key == pg.K_w or event.key == pg.K_UP or event.key == pg.K_SPACE:
                self.animation_phase = 0
                if event.type == pg.KEYUP:
                    self.jump = False
            if event.key == pg.K_e and self.special <= 0 and self.current_bug != 'Parasite':
                if self.stamina >= s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['COST']:
                    # play_sound(self.game, s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['SOUND'])
                    self.animation_phase = 0
                    self.special = s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['DURATION']
                    self.animation_type = s.Animation.SPECIAL_A
                    self.animation_speed = s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['SPEED']
                    self.stamina -= s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['COST']
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_j or event.key == pg.K_k or event.key == pg.K_l:
                if self.current_bug != 'Parasite':
                    self.attack_leniency = 0

    def handle_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            if self.attacking <= 0 and self.special <= 0:
                self.direction = 'Left'
                self.animation_type = s.Animation.WALK
            if self.attacking <= 0 and self.special <= 0:
                self.acc.x = -s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            if self.attacking <= 0 and self.special <= 0:
                self.direction = 'Right'
                self.animation_type = s.Animation.WALK
            if self.attacking <= 0 and self.special <= 0:
                self.acc.x = s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]:
            if self.jump == False and self.attacking <= 0 and self.special <= 0:
                self.jump_leniency = 0
                self.jump = True
        if keys[pg.K_s]:
            if self.jump and self.attacking <= 0 and self.special <= 0 and not self.in_air:
                self.pos.y += 30
                self.jump_leniency = -1
                self.jump = False
        if keys[pg.K_q] and pg.time.get_ticks() > self.parasite_cooldown:
            if self.attacking <= 0 and self.special <= 0:
                self.parasite_cooldown = pg.time.get_ticks() + 2000
                locked = False
                for enemy in self.game.enemies:
                    if self.pos.distance_squared_to(enemy.pos) < 150**2 and enemy.controllable and not locked:
                        if len(self.game.arena_enemies) > 0:
                            if enemy not in self.game.arena_enemies:
                                return
                        if self.current_bug != 'Parasite':
                            host = Enemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
                            if len(self.game.arena_enemies) >= 1:
                                self.game.arena_enemies.add(host)
                        locked = True
                        Projectile(self.game, self.pos.x, self.pos.y, 'Parasite', 150, enemy.pos, 0.5, -0.05, 5000, 0, True, True)
                        self.current_bug = enemy.bug_type
                        self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
                        self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
                        self.stamina = self.max_stamina
                        self.animation_type = s.Animation.IDLE
                        self.image = self.game.all_images[self.current_bug][self.animation_type][0]
                        self.rect = self.image.get_rect()
                        self.hit_rect = pg.Rect.copy(s.BUGS[self.current_bug]['HIT_RECT'])
                        self.pos = enemy.pos
                        self.rect.center = self.pos
                        self.hit_rect.center = self.pos
                        self.image = enemy.image
                        enemy.kill()

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.current_bug][self.animation_type]):
            if self.attacking <= 0:
                self.animation_phase = 0
            else:
                self.animation_phase = len(self.game.all_images[self.current_bug][self.animation_type]) - 1
        self.image = self.game.all_images[self.current_bug][self.animation_type][self.animation_phase]
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed
        if self.direction == 'Left':
            self.image = pg.transform.flip(self.image, True, False)

    def draw_ui(self):
        BAR_LENGTH = 120
        BAR_HEIGHT = 20
        percent = self.health / self.max_health
        fill = percent * BAR_LENGTH
        outline_rect = pg.Rect(5, 5, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(5, 5, fill, BAR_HEIGHT)
        pg.draw.rect(self.game.screen, s.BLUE, fill_rect)
        pg.draw.rect(self.game.screen, s.BLACK, outline_rect, 2)
        write_text(self.game, 'Health', 20, s.BLACK, (10, 10))
        if self.max_stamina > 0:
            BAR_LENGTH = 120
            BAR_HEIGHT = 20
            percent = self.stamina / self.max_stamina
            fill = percent * BAR_LENGTH
            outline_rect = pg.Rect(5, 25, BAR_LENGTH, BAR_HEIGHT)
            fill_rect = pg.Rect(5, 25, fill, BAR_HEIGHT)
            if percent > 0.6:
                col = s.GREEN
            elif percent > 0.3:
                col = s.YELLOW
            else:
                col = s.RED
            pg.draw.rect(self.game.screen, col, fill_rect)
            pg.draw.rect(self.game.screen, s.BLACK, outline_rect, 2)
            write_text(self.game, 'Stamina', 20, s.BLACK, (10, 30))
        if self.current_bug != 'Parasite':
            rect = self.game.icon.get_rect()
            rect.midbottom = self.hit_rect.midtop
            self.game.screen.blit(self.game.icon, self.game.camera.apply_rect(rect))
        if len(self.game.arena_enemies) > 0:
            write_text(self.game, 'Ambush! Kill all hostiles!', 32, s.RED, (s.WIDTH / 4 - 30, 10))
            write_text(self.game, 'Hostiles Left: ' + str(len(self.game.arena_enemies)), 32, s.RED, (s.WIDTH / 4 + 40, 30))

    def check_collision(self):
        # check collision x
        self.hit_rect.centerx = self.pos.x
        if collide_with_walls(self, self.game.walls, 'x'):
            self.vel.x = 0
            self.acc.x = 0
        # check collision y
        self.hit_rect.centery = self.pos.y
        hit = collide_with_walls(self, self.game.walls, 'y')
        if hit:
            self.acc.y = 0
            self.vel.y = 0
            self.platform = hit
            self.in_air = False
        else:
            self.in_air = True
        # check collision with semi-solid walls
        if self.vel.y >= 0:
            hit = collide_with_walls(self, self.game.semi_walls, 'y', False)
            if hit:
                self.acc.y = 0
                self.vel.y = 0
                self.platform = hit
                self.in_air = False

    def hit(self, damage):
        self.attacking = s.PLAYER_STUN
        self.special = 0
        if self.current_bug != 'Parasite':
            self.animation_type = s.Animation.HIT
        self.health -= damage
        if self.health <= 0:
            self.kill()
            self.checkpoint.respawn()
        play_sound(self.game, 'Hit' + str(rand.randrange(1, 7)))

    def set_pos(self, x, y):
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.hit_rect = pg.Rect.copy(s.BUGS[self.current_bug]['HIT_RECT'])
        self.hit_rect.center = self.rect.center

    def attacks(self):
        # attacking countdown
        if self.attacking > 0:
            self.attacking -= 1
            if self.attacking <= 0:
                self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
                self.animation_type = s.Animation.IDLE
        # check for special attacks
        if self.special > 0 and self.current_bug != 'Parasite':
            self.special -= 1
            special_attacks[self.current_bug](self, self.special)
        # do attack if on ground
        if self.attack_leniency >= 0:
            self.attack_leniency += 1
        if 0 < self.attack_leniency <= 10 and not self.in_air and self.attacking <= 0 and self.current_bug != 'Parasite':
            # play_sound(self.game, s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['SOUND'])
            self.animation_phase = 0
            self.attacking = s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['DURATION']
            self.animation_type = self.attack_type
            self.animation_speed = s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['SPEED']
            rect = pg.Rect.copy(s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['HIT_RECT'])
            offset = s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['OFFSET']
            rect.center = self.pos + offset
            if self.direction == 'Left':
                if self.attack_type == s.Animation.FRONT_A:
                    rect.center = self.pos - offset
                else:
                    rect.centerx = self.pos.x - offset.x
            # for debug
            self.game.debug_rects.append(rect)
            for enemy in self.game.enemies:
                if pg.Rect.colliderect(rect, enemy.hit_rect):
                    enemy.hit(s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['DAMAGE'])
            if self.current_bug == 'Bombardier' and self.attack_type == s.Animation.FRONT_A and len(self.game.acid) < 3:
                Projectile(self.game, rect.centerx, rect.centery, 'Bombardier', 100, vec(rect.centerx, rect.centery), 0, 0, 10000,
                           s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['DAMAGE'], False, 500, True, 20, True)
            self.attack_leniency = -1

    def update(self):
        # temporary stamina drain, probably rework later
        if self.max_stamina > 0:
            self.stamina -= 0.05
        if self.stamina < 0:
            host = Enemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
            if len(self.game.arena_enemies) >= 1:
                self.game.arena_enemies.add(host)
            self.current_bug = 'Parasite'
            self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
            self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
            self.stamina = self.max_stamina
            self.animation_type = s.Animation.IDLE
            self.attacking = 0
            self.image = self.game.all_images[self.current_bug][self.animation_type][0]
            self.rect = self.image.get_rect()
            self.hit_rect = pg.Rect.copy(s.BUGS[self.current_bug]['HIT_RECT'])
        self.acc.x = 0
        self.attacks()
        self.handle_keys()
        # apply gravity
        if self.in_air == True:
            self.acc.y += s.BUGS[self.current_bug]['GRAVITY']
            if self.acc.y >= s.BUGS[self.current_bug]['MAX_FALL']:
                self.acc.y = s.BUGS[self.current_bug]['MAX_FALL']
        # allow leniency for inputs
        if self.jump_leniency >= 0:
            self.jump_leniency += 1
        if self.attacking <= 0 and self.special <= 0:
            if 0 < self.jump_leniency < 10 and self.in_air == False:
                play_sound(self.game, 'jump')
                self.acc.y = s.BUGS[self.current_bug]['JUMP_ACC']
                self.in_air = True
        # apply friction
        self.acc.x += self.vel.x * s.BUGS[self.current_bug]['FRICTION']
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.check_collision()
        self.rect.center = self.pos
        # animation
        self.animate_movement()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, solid=True, visible=False):
        self.groups = game.walls
        if not solid:
            self.groups = game.semi_walls
        self.solid = solid
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        if visible:
            self.groups = game.walls, game.all_sprites
            self.image = self.game.vine
            self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hit_rect = self.rect
        pg.sprite.Sprite.__init__(self, self.groups)


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, type, controllable=True):
        self.bug_type = type
        self.controllable = controllable
        self.game = game
        self.groups = self.game.all_sprites, self.game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.attack_type = s.Animation.FRONT_A
        self.planned_attack = s.Animation.FRONT_A
        self.animation_type = s.Animation.WALK
        self.direction = 'Right'
        self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = pg.Rect.copy(s.BUGS[self.bug_type]['HIT_RECT'])
        self.hit_rect.center = self.rect.center
        self.in_air = False
        self.jumping = True
        self.next_animation_tick = 0
        self.max_health = s.BUGS[self.bug_type]['HEALTH']
        self.health = self.max_health
        self.planning = 0
        self.attacking = 0
        self.stunned = -1
        self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']
        self.recent_damage = 0
        self.clear_damage = 0
        self.platform = Obstacle(self.game, 0, 0, 0, 0)
        self.anger = 0

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.bug_type][self.animation_type]):
            if self.stunned >= 0 or self.attacking > 0:
                self.animation_phase = len(self.game.all_images[self.bug_type][self.animation_type]) - 1
            else:
                self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][self.animation_phase]
        if self.direction == 'Left':
            self.image = pg.transform.flip(self.image, True, False)
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed

    def check_collision(self):
        # check collision y
        self.hit_rect.centery = self.pos.y
        hit = collide_with_walls(self, self.game.walls, 'y')
        if hit:
            self.acc.y = 0
            self.vel.y = 0
            self.platform = hit
            self.in_air = False
            self.jumping = False
        else:
            self.in_air = True
        # check collision with semi-solid walls
        if self.acc.y >= 0:
            hit = collide_with_walls(self, self.game.semi_walls, 'y', False)
            if hit:
                self.jumping = False
                self.acc.y = 0
                self.vel.y = 0
                self.platform = hit
                self.in_air = False
        # check collision x
        self.hit_rect.centerx = self.pos.x
        if collide_with_walls(self, self.game.walls, 'x'):
            self.vel.x = 0
            self.acc.x = 0
            if self.direction == 'Right':
                self.direction = 'Left'
            else:
                self.direction = 'Right'
            if self.anger > 0:
                if not self.jumping and self.pos.y > self.game.player.pos.y:
                    self.acc.y = s.BUGS[self.bug_type]['JUMP_ACC'] - 0.5
                    self.jumping = True
                    self.in_air = True

    def hit(self, damage, not_stun=False):
        if not_stun:
            self.health -= damage
            self.clear_damage = pg.time.get_ticks() + 2000
            self.recent_damage += damage
            if self.health <= 0:
                if self.game.player.health < s.HEALTH - 50:
                    self.game.player.health += 50
                play_sound(self.game, 'death')
                self.kill()
            play_sound(self.game, 'Hit' + str(rand.randrange(1, 7)))
        else:
            self.pos.y -= 10
            self.acc = vec(0, 0)
            self.vel = vec(0, 0)
            self.health -= damage
            self.planning = 0
            self.attacking = 0
            self.clear_damage = pg.time.get_ticks() + 2000
            self.recent_damage += damage
            if self.health <= 0:
                if self.game.player.health < s.HEALTH - 50:
                    self.game.player.health += 50
                play_sound(self.game, 'death')
                self.kill()
            self.animation_type = s.Animation.HIT
            self.animation_phase = 0
            self.stunned = s.BUGS[self.bug_type]['RECOVERY']
            play_sound(self.game, 'Hit' + str(rand.randrange(1, 7)))
            if self.recent_damage >= s.BUGS[self.bug_type]['STUN']:
                self.recent_damage = 0
                self.stunned = -1
                self.vel = vec(20, 20)
                if self.game.player.direction == 'Left':
                    self.vel = -vec(20, 20)

    def wander(self):
        self.animation_type = s.Animation.WALK
        if self.platform.rect.left > self.hit_rect.left:
            self.direction = 'Right'
        if self.platform.rect.right < self.hit_rect.right:
            self.direction = 'Left'

    def chase(self):
        self.animation_type = s.Animation.WALK
        if self.anger > 0:
            self.anger -= 1
            if self.pos.distance_squared_to(self.game.player.pos) > 64 ** 2:
                if self.game.player.pos.x < self.pos.x:
                    self.direction = 'Left'
                else:
                    self.direction = 'Right'
            if self.platform.rect.left > self.hit_rect.left or self.platform.rect.right < self.hit_rect.right:
                if self.jumping == False and self.pos.y > self.game.player.pos.y:
                    self.acc.y = s.BUGS[self.bug_type]['JUMP_ACC'] - 0.5
                    self.jumping = True
                    self.in_air = True
            if self.game.player.pos.y - self.pos.y < -20:
                rect = pg.Rect(self.pos.x, self.rect.top - 128, 1, 128)
                for wall in self.game.semi_walls:
                    if rect.colliderect(wall.rect) and self.jumping == False:
                        self.acc.y = s.BUGS[self.bug_type]['JUMP_ACC'] - 0.5
                        self.jumping = True
                        self.in_air = True
            elif self.game.player.pos.y - self.pos.y > 20:
                if not self.platform.solid:
                    self.pos.y += 1
            if rand.randrange(0, 3) == 0:
                rect = pg.Rect.copy(s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['HIT_RECT'])
                offset = s.BUGS[self.bug_type]['ATTACKS'][self.attack_type]['OFFSET']
                rect.center = self.pos + offset
                if self.direction == 'Left':
                    if self.attack_type == s.Animation.FRONT_A:
                        rect.center = self.pos - offset
                    else:
                        rect.centerx = self.pos.x - offset.x
                if self.game.player.rect.colliderect(rect) and self.stunned < 0 and self.planning < -100:
                    self.vel = vec(0, 0)
                    self.acc = vec(0, 0)
                    self.planning = 60
        if self.game.player.platform == self.platform or self.pos.distance_squared_to(self.game.player.pos) < 96 ** 2:
            if self.anger == 0:
                if self.game.player.pos.x < self.pos.x:
                    self.direction = 'Left'
                else:
                    self.direction = 'Right'
                self.stunned = 20
                self.planned_attack = rand.choice([s.Animation.FRONT_A, s.Animation.DOWN_A, s.Animation.UP_A])
                self.acc.x = 0
                self.vel = vec(0, 0)
            self.anger = 300

    def attack(self):
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.attacking -= 1
        if self.attacking <= 0:
            self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']
            self.animation_type = s.Animation.IDLE

    def update(self):
        if self.stunned >= 0:
            self.stunned -= 1
            self.animation_speed = s.BUGS[self.bug_type]['RECOVERY']
        elif self.planning <= 0 and self.attacking <= 0:
            self.wander()
            self.chase()
            # movement
            self.acc.x = 0
            if self.direction == 'Right':
                self.acc.x = s.BUGS[self.bug_type]['ACC']
            elif self.direction == 'Left':
                self.acc.x = -s.BUGS[self.bug_type]['ACC']
            if self.anger <= 0:
                self.acc.x /= 2
            self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']
        # apply gravity
        if self.in_air == True:
            self.acc.y += s.BUGS[self.bug_type]['GRAVITY']
            if self.acc.y >= s.BUGS[self.bug_type]['MAX_FALL']:
                self.acc.y = s.BUGS[self.bug_type]['MAX_FALL']
        # apply friction
        self.acc.x += self.vel.x * s.BUGS[self.bug_type]['FRICTION']
        # perform attack
        self.planning -= 1
        if self.planning > 0:
            self.acc = vec(0, 0)
            self.vel = vec(0, 0)
            self.animation_type = s.Animation.IDLE
            if rand.randrange(0, self.planning) == 30 or self.planning == 1:
                self.planning = 0
                # play_sound(self.game, s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['SOUND'])
                self.animation_phase = 0
                self.attacking = s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['DURATION']
                self.animation_type = self.planned_attack
                self.animation_speed = s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['SPEED']
                rect = pg.Rect.copy(s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['HIT_RECT'])
                offset = s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['OFFSET']
                rect.center = self.pos + offset
                if self.direction == 'Left':
                    if self.planned_attack == s.Animation.FRONT_A:
                        rect.center = self.pos - offset
                    else:
                        rect.centerx = self.pos.x - offset.x
                if pg.Rect.colliderect(rect, self.game.player.hit_rect):
                    self.game.player.hit(s.BUGS[self.bug_type]['ATTACKS'][self.planned_attack]['DAMAGE'])
                self.planned_attack = rand.choice([s.Animation.FRONT_A, s.Animation.DOWN_A, s.Animation.UP_A])
                self.game.debug_rects.append(rect)
        if self.clear_damage < pg.time.get_ticks():
            self.recent_damage = 0
        if self.attacking > 0:
            self.attack()
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.check_collision()
        self.rect.center = self.pos
        self.animate_movement()


class Turret(pg.sprite.Sprite):
    def __init__(self, game, x, y, health, damage, frequency, speed, target, die_on_impact, direction, flip_vert, flip_hor, size):
        self.groups = game.all_sprites, game.enemies
        self.game = game
        self.animation_type = s.Animation.IDLE
        self.image = self.game.all_images['Turret'][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center
        self.die_on_impact = die_on_impact
        self.health = health
        self.damage = damage
        self.next_animation_tick = 0
        self.next_fire = 0
        self.frequency = frequency
        self.speed = speed
        self.flip_vert = flip_vert
        self.flip_hor = flip_hor
        self.size = size / 2
        if direction == 'Up':
            self.animation_type = s.Animation.WALK
        if target == self.game.player.pos:
            self.target = 'player'
            self.animation_type = s.Animation.HIT
        else:
            self.target = target
        self.controllable = False
        self.animation_phase = -1
        self.animate()
        pg.sprite.Sprite.__init__(self, self.groups)

    def hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
        play_sound(self.game, 'Hit' + str(rand.randrange(1, 7)))

    def animate(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images['Turret'][self.animation_type]):
            self.animation_phase = 0
        self.image = self.game.all_images['Turret'][self.animation_type][self.animation_phase]
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + 300
        if self.flip_hor:
            self.image = pg.transform.flip(self.image, True, False)
        if self.flip_vert:
            self.image = pg.transform.flip(self.image, False, True)

    def update(self):
        if self.pos.distance_squared_to(self.game.player.pos) < self.size**2:
            self.animate()
            if pg.time.get_ticks() > self.next_fire:
                target = self.target
                if target == 'player':
                    target = self.game.player.pos
                if self.die_on_impact:
                    Projectile(self.game, self.pos.x, self.pos.y, 'Turret', 150, target, self.speed, -0.5, 5000, self.damage, self.die_on_impact)
                else:
                    Projectile(self.game, self.pos.x, self.pos.y, 'Turret', 150, target, self.speed, -0.5, 5000, self.damage, self.die_on_impact, 100, False, 10)
                self.next_fire = pg.time.get_ticks() + self.frequency


class Projectile(pg.sprite.Sprite):
    def __init__(self, game, x, y, name, animation, target, acceleration, stop_speed, time, damage, die_on_impact=True, hit_speed=0, friendly=False, hits=0, not_stun=False):
        self.game = game
        self.name = name
        self.groups = self.game.all_sprites, self.game.projectiles
        if not_stun:
            self.groups = self.game.all_sprites, self.game.projectiles, self.game.acid
        pg.sprite.Sprite.__init__(self, self.groups)
        self.animation_phase = 0
        self.image = self.game.all_images[name][s.Animation.PROJECTILE][0]
        self.og_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.next_animation_tick = 0
        self.animation_speed = animation
        self.target = target
        self.acceleration = acceleration
        self.slowing = stop_speed
        self.time_left = pg.time.get_ticks() + time
        self.die_on_impact = die_on_impact
        self.damage = damage
        self.friendly = friendly
        self.hits = hits
        self.hit_speed = hit_speed
        self.next_hit = 0
        self.angle = 180
        self.not_stun = not_stun

    def rotate(self):
        rel_x, rel_y = (self.target.x - self.rect.x), (self.target.y - self.rect.y)
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90

    def hit_object(self, object):
        if pg.time.get_ticks() < self.next_hit:
            return
        self.next_hit = pg.time.get_ticks() + self.hit_speed
        object.hit(self.damage, self.not_stun)
        self.hits -= 1
        if self.hits <= 0:
            self.kill()

    def update(self):
        if self.friendly:
            hits = pg.sprite.spritecollide(self, self.game.enemies, False)
            for hit in hits:
                self.hit_object(hit)
        if pg.time.get_ticks() > self.time_left:
            self.kill()
        # accelerate towards target
        if self.pos.distance_squared_to(self.target) > 5:
            self.rotate()
            self.image = pg.transform.rotate(
                self.og_image, int(self.angle))
            if self.pos.x < self.target.x:
                self.acc.x = self.acceleration
            elif self.pos.x > self.target.x:
                self.acc.x = -self.acceleration
            if self.pos.y < self.target.y:
                self.acc.y = self.acceleration
            elif self.pos.y > self.target.y:
                self.acc.y = -self.acceleration
        else:
            self.acc = vec(0, 0)
            self.vel = vec(0, 0)
            if self.die_on_impact:
                self.kill()
        # equations of motion
        self.acc += self.vel * self.slowing
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos


class Arena(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, waves, enemy_amount, enemy_type, enemy_location):
        self.groups = game.all_sprites
        self.game = game
        self.image = pg.Surface((0, 0))
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.hit_rect = self.rect
        self.total_waves = waves
        self.wave_count = -1
        self.enemies_per_wave = enemy_amount
        self.enemy_type_per_wave = enemy_type
        self.enemy_locations = enemy_location
        self.activated = False
        self.border = []
        pg.sprite.Sprite.__init__(self, self.groups)

    def spawn_wave(self):
        play_sound(self.game, 'alarm')
        self.wave_count += 1
        if self.wave_count >= self.total_waves:
            for border in self.border:
                border.kill()
            self.kill()
            return
        enemy_types = self.enemy_type_per_wave[self.wave_count].split(',')
        # temp dynamic spawning, fix later
        added = self.game.player.health // 500
        for i in range(int(self.enemies_per_wave[self.wave_count]) + added):
            name = rand.choice(enemy_types)
            location = rand.choice(self.enemy_locations)
            self.game.arena_enemies.add(Enemy(self.game, location.x, location.y, name))

    def draw_ui(self):
        write_text(self.game, 'Ambush!', 32, s.RED, (0, s.WIDTH / 4))

    def update(self):
        if pg.Rect.colliderect(self.rect, self.game.player.hit_rect) and self.activated == False:
            self.border.append(Obstacle(self.game, self.x - 48, 0, 32, self.rect.height, True, True))
            self.border.append(Obstacle(self.game, self.x + self.rect.width + 16, 0, 32, self.rect.height, True, True))
            self.spawn_wave()
            self.activated = True
        if self.activated:
            if len(self.game.arena_enemies) == 0:
                self.spawn_wave()
            else:
                spawn = True
                for enemy in self.game.arena_enemies:
                    if enemy.controllable:
                        spawn = False
                if spawn:
                    loc = rand.choice(self.enemy_locations)
                    enemy = Enemy(self.game, loc.x, loc.y, 'Roach')
                    self.game.arena_enemies.add(enemy)


class Pit(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, destination):
        self.groups = game.pits, game.all_sprites
        self.game = game
        self.image = pg.Surface((0, 0))
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.destination = destination
        pg.sprite.Sprite.__init__(self, self.groups)

    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in hits:
            if self.hit_rect.colliderect(enemy.hit_rect):
                enemy.hit(s.PIT_DAMAGE)
                enemy.pos = vec(self.destination.x, self.destination.y)
                enemy.rect.center = enemy.pos
                enemy.hit_rect = pg.Rect.copy(s.BUGS[enemy.bug_type]['HIT_RECT'])
                enemy.hit_rect.center = enemy.rect.center


class Checkpoint(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.checkpoints
        self.game = game
        self.image = self.game.dead_checkpoint
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.centerx = x
        self.rect.centery = y
        self.saved_health = 0
        self.saved_stamina = 0
        self.saved_bug = 'Parasite'
        self.activated = False
        self.tint = pg.Surface((s.WIDTH, s.HEIGHT))
        self.tint.fill(s.BLACK)
        pg.sprite.Sprite.__init__(self, self.groups)

    def activate(self):
        if not self.activated:
            play_sound(self.game, 'checkpoint')
            self.saved_health = self.game.player.health
            self.saved_bug = self.game.player.current_bug
            self.saved_stamina = self.game.player.stamina
            self.image = self.game.alive_checkpoint
            self.rect = self.image.get_rect()
            self.hit_rect = self.rect
            self.rect.centerx = self.x
            self.rect.centery = self.y
            self.activated = True

    def draw_tint(self, alpha):
        self.tint.set_alpha(alpha)
        self.game.screen.blit(self.tint, (0, 0))

    def respawn(self):
        pg.mixer.music.pause()
        play_sound(self.game, 'player_death')
        for alpha in range(0, 255, 8):
            self.draw_tint(alpha)
            pg.display.flip()
            time.sleep(0.05)
        self.game.load_map(self.game.current_map, 'player')
        self.game.player.image = self.game.all_images[self.saved_bug][s.Animation.IDLE][0]
        self.game.player.rect = self.game.player.image.get_rect()
        self.game.player.health = self.saved_health
        self.game.player.current_bug = self.saved_bug
        self.game.player.set_pos(self.rect.topleft[0], self.rect.topleft[1])
        self.game.player.animation_type = s.Animation.IDLE
        pg.mixer.music.unpause()


class Teleport(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, mission):
        self.groups = game.teleports
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y
        self.hit_rect = self.rect
        self.mission = mission


class Button(pg.sprite.Sprite):
    def __init__(self, ui, pos, size, text, text_size, offset, color, state, border=0, circle=0):
        self.ui = ui
        self.rect = pg.Rect(pos, size)
        self.offset = offset
        self.text = text
        self.text_size = text_size
        self.color = color
        self.state = state
        self.border = border
        self.rounding = min(size[0], size[1]) // circle
        self.groups = self.ui.buttons
        pg.sprite.Sprite.__init__(self, self.groups)

    def draw(self):
        pg.draw.rect(self.ui.game.screen, self.color, self.rect, self.border, self.rounding)
        pos = (self.rect.x + self.offset[0], self.rect.y + self.offset[1])
        write_text(self.ui.game, self.text, self.text_size, s.WHITE, pos)

    def click(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.ui.state = self.state
