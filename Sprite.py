# Sprite classes for platform game
from os import write
import pygame as pg
import random as rand
import math
import Settings as s
from Display import collide_hit_rect
vec = pg.math.Vector2


def roach_special(player, count):
    if count == 30:
        for i in range(-20, 20, 10):
            target = player.pos + vec(20, i)
            if player.direction == 'Left':
                target = player.pos + vec(-20, i)
            damage = s.BUGS[player.current_bug]['ATTACKS'][player.attack_type]['DAMAGE']
            Projectile(player.game, player.pos.x, player.pos.y, 'Roach', 150, target, 0.5, 0, 200, damage, True, 200, True, 4)
    if count <= 0:
        player.animation_speed = s.BUGS[player.current_bug]['ANIMATION']
        player.animation_type = s.Animation.IDLE


special_attacks = {
    'Roach': roach_special
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
                    elif hit.rect.top > sprite.rect.bottom:
                        collided = True
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

    def handle_events(self, event=pg.event.Event):
        # Only update variables if key pressed
        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            # Update direction
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.FRONT_A
                else:
                    self.animation_type = s.Animation.IDLE
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.FRONT_A
                else:
                    self.animation_type = s.Animation.IDLE
            if event.key == pg.K_UP or event.key == pg.K_w:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.UP_A
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                if event.type == pg.KEYDOWN:
                    self.attack_type = s.Animation.DOWN_A
            if event.key == pg.K_SPACE:
                self.animation_phase = 0
                if event.type == pg.KEYUP:
                    self.jump = False
            if event.key == pg.K_e and self.special <= 0 and self.current_bug != 'Parasite':
                if self.stamina >= s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['COST']:
                    play_sound(self.game, s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['SOUND'])
                    self.animation_phase = 0
                    self.special = s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['DURATION']
                    self.animation_type = s.Animation.SPECIAL_A
                    self.animation_speed = s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['SPEED']
                    self.stamina -= s.BUGS[self.current_bug]['ATTACKS'][s.Animation.SPECIAL_A]['COST']
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.current_bug != 'Parasite':
                self.attack_leniency = 0

    def handle_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            if self.attacking <= 0 and self.special <= 0:
                self.direction = 'Left'
                self.animation_type = s.Animation.WALK
            self.acc.x = -s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            if self.attacking <= 0 and self.special <= 0:
                self.direction = 'Right'
                self.animation_type = s.Animation.WALK
            self.acc.x = s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_SPACE]:
            if self.jump == False:
                self.jump_leniency = 0
                self.jump = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            if self.jump and not self.in_air:
                self.pos.y += 1
                self.jump_leniency = -1
                self.jump = False
        if keys[pg.K_q] and pg.time.get_ticks() > self.parasite_cooldown:
            self.parasite_cooldown = pg.time.get_ticks() + 2000
            locked = False
            for enemy in self.game.enemies:
                if self.pos.distance_squared_to(enemy.pos) < 150**2 and enemy.controllable and not locked:
                    if self.current_bug != 'Parasite':
                        Enemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
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

    def check_collision(self):
        # check collision x
        self.hit_rect.centerx = self.pos.x
        if collide_with_walls(self, self.game.walls, 'x'):
            self.vel.x = 0
            self.acc.x = 0
        # check collision y
        self.hit_rect.centery = self.pos.y
        if collide_with_walls(self, self.game.walls, 'y'):
            self.acc.y = 0
            self.vel.y = 0
            self.in_air = False
        else:
            self.in_air = True
        # check collision with semi-solid walls
        if self.acc.y >= 0:
            if collide_with_walls(self, self.game.semi_walls, 'y', False):
                self.acc.y = 0
                self.vel.y = 0
                self.in_air = False

    def hit(self, damage):
        self.attacking = s.PLAYER_STUN
        if self.current_bug != 'Parasite':
            self.animation_type = s.Animation.HIT
        self.health -= damage
        if self.health <= 0:
            self.kill()
        play_sound(self.game, self.current_bug + 'Hit')

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
            play_sound(self.game, s.BUGS[self.current_bug]['ATTACKS'][self.attack_type]['SOUND'])
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
            self.attack_leniency = -1

    def update(self):
        # temporary stamina drain, probably rework later
        if self.max_stamina > 0:
            self.stamina -= 0.05
        if self.stamina < 0:
            Enemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
            self.current_bug = 'Parasite'
            self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
            self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
            self.stamina = self.max_stamina
            self.animation_type = s.Animation.IDLE
            self.attacking = 0
            self.image = self.game.all_images[self.current_bug][self.animation_type][0]
            self.rect = self.image.get_rect()
            self.hit_rect = pg.Rect.copy(s.BUGS[self.current_bug]['HIT_RECT'])
        self.attacks()
        self.acc.x = 0
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
                self.acc.y = s.BUGS[self.current_bug]['JUMP_ACC']
                self.in_air = True
            # apply friction
            self.acc.x += self.vel.x * s.BUGS[self.current_bug]['FRICTION']
            # equations of motion
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc
            self.check_collision()
            self.rect.center = self.pos
        self.animate_movement()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, solid=True):
        self.groups = game.walls
        if not solid:
            self.groups = game.semi_walls
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
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
        self.animation_type = s.Animation.IDLE
        self.direction = 'Right'
        self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = pg.Rect.copy(s.BUGS[self.bug_type]['HIT_RECT'])
        self.hit_rect.center = self.rect.center
        self.in_air = False
        self.next_animation_tick = 0
        self.max_health = s.BUGS[self.bug_type]['HEALTH']
        self.health = self.max_health
        self.attacking = 0
        self.stunned = -1
        self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']
        self.recent_damage = 0
        self.clear_damage = 0

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.bug_type][self.animation_type]):
            if self.stunned >= 0:
                self.animation_phase = len(self.game.all_images[self.bug_type][self.animation_type]) - 1
            else:
                self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][self.animation_phase]
        if self.direction == 'Left':
            self.image = pg.transform.flip(self.image, True, False)
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed

    def check_collision(self):
        # check collision x
        self.hit_rect.centerx = self.pos.x
        if collide_with_walls(self, self.game.walls, 'x'):
            self.vel.x = 0
            self.acc.x = 0
        # check collision y
        self.hit_rect.centery = self.pos.y
        if collide_with_walls(self, self.game.walls, 'y'):
            self.acc.y = 0
            self.vel.y = 0
            self.in_air = False
        else:
            self.in_air = True
        # check collision with semi-solid walls
        if self.acc.y >= 0:
            if collide_with_walls(self, self.game.semi_walls, 'y', False):
                self.acc.y = 0
                self.vel.y = 0
                self.in_air = False

    def hit(self, damage):
        self.health -= damage
        self.clear_damage = pg.time.get_ticks() + 2000
        self.recent_damage += damage
        if self.health <= 0:
            self.kill()
        self.animation_type = s.Animation.HIT
        self.animation_phase = 0
        self.stunned = s.BUGS[self.bug_type]['RECOVERY']
        play_sound(self.game, self.bug_type + 'Hit')
        if self.recent_damage >= s.BUGS[self.bug_type]['STUN']:
            self.recent_damage = 0
            self.stunned = -1
            self.vel = vec(20, 20)
            if self.game.player.direction == 'Left':
                self.vel = -vec(20, 20)

    def update(self):
        if self.clear_damage < pg.time.get_ticks():
            self.recent_damage = 0
        elif self.recent_damage >= 0:
            pos = self.game.camera.apply_point(self.pos)
            write_text(self.game, str(self.recent_damage), 20, s.RED, (pos.x + 30, pos.y))
        # apply gravity
        if self.in_air == True:
            self.acc.y += s.BUGS[self.bug_type]['GRAVITY']
            if self.acc.y >= s.BUGS[self.bug_type]['MAX_FALL']:
                self.acc.y = s.BUGS[self.bug_type]['MAX_FALL']
        if self.stunned >= 0:
            self.stunned -= 1
            self.animation_speed = s.BUGS[self.bug_type]['RECOVERY']
        else:
            # random movement
            self.acc.x = 0
            self.animation_type = s.Animation.IDLE
            chance = rand.randrange(1, 11)
            if chance == 1 and self.in_air == False:
                self.acc.y = s.BUGS[self.bug_type]['JUMP_ACC']
                self.in_air = True
            if chance <= 4:
                self.acc.x = -s.BUGS[self.bug_type]['ACC']
                self.direction = 'Left'
                self.animation_type = s.Animation.WALK
            elif chance >= 6:
                self.direction = 'Right'
                self.animation_type = s.Animation.WALK
                self.acc.x = s.BUGS[self.bug_type]['ACC']
            self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']
            self.stunned = -1
            if rand.randrange(1, 1000) == 1:
                Projectile(self.game, self.pos.x, self.pos.y, 'Roach', 150, self.game.player.pos, 0.1, -0.05, 5000, 50)
            # apply friction
            self.acc.x += self.vel.x * s.BUGS[self.bug_type]['FRICTION']
            # equations of motion
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc
            self.check_collision()
            self.rect.center = self.pos
        self.animate_movement()


class Projectile(pg.sprite.Sprite):
    def __init__(self, game, x, y, name, animation, target, acceleration, stop_speed, time, damage, die_on_impact=True, hit_speed=0, friendly=False, hits=0):
        self.game = game
        self.groups = self.game.all_sprites, self.game.projectiles
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

    def animate(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.current_bug][self.animation_type]):
            self.animation_phase = 0
        self.image = self.game.all_images[self.current_bug][self.animation_type][self.animation_phase]
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed
        if self.direction == 'Left':
            self.image = pg.transform.flip(self.image, True, False)

    def rotate(self):
        rel_x, rel_y = (self.target.x - self.rect.x),\
            (self.target.y - self.rect.y)
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90

    def hit_object(self, object):
        if pg.time.get_ticks() < self.next_hit:
            return
        self.next_hit = pg.time.get_ticks() + self.hit_speed
        object.hit(self.damage)
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
        self.total_waves = waves
        self.wave_count = -1
        self.enemies_per_wave = enemy_amount
        self.enemy_type_per_wave = enemy_type
        self.enemy_locations = enemy_location
        self.activated = False
        self.border = []
        self.enemies = pg.sprite.Group()
        pg.sprite.Sprite.__init__(self, self.groups)

    def spawn_wave(self):
        self.wave_count += 1
        if self.wave_count >= self.total_waves:
            for border in self.border:
                border.kill()
            self.kill()
            return
        enemy_types = self.enemy_type_per_wave[self.wave_count].split(',')
        # temp dynamic spawning, fix later
        added = self.game.player.health // 5000
        for i in range(int(self.enemies_per_wave[self.wave_count]) + added):
            name = rand.choice(enemy_types)
            location = rand.choice(self.enemy_locations)
            self.enemies.add(Enemy(self.game, location.x, location.y, name))

    def update(self):
        if pg.Rect.colliderect(self.rect, self.game.player.hit_rect) and self.activated == False:
            self.border.append(Obstacle(self.game, self.x - 32, self.y, 32, self.rect.height))
            self.border.append(Obstacle(self.game, self.x + self.rect.width, self.y, 32, self.rect.height))
            self.spawn_wave()
            self.activated = True
        if len(self.enemies) == 0 and self.activated:
            self.spawn_wave()


class Pit(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, destinationx, destinationy):
        self.groups = game.pits
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.destinationx = destinationx
        self.destinationy = destinationy
        pg.sprite.Sprite.__init__(self, self.groups)


class Teleport(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, playerDestination, playerLocation):
        self.groups = game.teleports
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.rect.x = x
        self.rect.y = y
        self.destination = playerDestination
        self.location = playerLocation
