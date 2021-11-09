# Sprite classes for platform game
import pygame as pg
import Settings as s
from Display import collide_hit_rect
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir, solid=True):
    collided = False
    if dir == 'x':
        hits = pg.sprite.spritecollide(
            sprite, group, False, collide_hit_rect)
        if hits:
            for hit in hits:
                if hit != sprite:
                    collided = True
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
                        collided = True
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


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.current_bug = 'Parasite'
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.is_moving = False
        self.attack_facing = s.Attacks.RIGHT_A
        self.animation_type = s.Animation.IDLE_RIGHT
        self.direction = s.Animation.IDLE_RIGHT
        self.animation_phase = 0
        self.image = self.game.all_images[self.current_bug][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
        self.hit_rect.center = self.rect.center
        self.jump = False
        self.jump_leniency = -1
        self.in_air = False
        self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
        self.stamina = self.max_stamina
        self.next_animation_tick = 0
        self.parasite_cooldown = 0
        self.attacking = 0
        self.attack_leniency = -1
        self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']

    def handle_events(self, event=pg.event.Event):
        # Only update variables if key pressed
        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            # Update direction
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Attacks.LEFT_A
                else:
                    self.animation_type = s.Animation.IDLE_LEFT
                    self.direction = s.Animation.IDLE_LEFT
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Attacks.RIGHT_A
                else:
                    self.animation_type = s.Animation.IDLE_RIGHT
                    self.direction = s.Animation.IDLE_RIGHT
            if event.key == pg.K_UP or event.key == pg.K_w:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Attacks.UP_A
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Attacks.DOWN_A
            if event.key == pg.K_SPACE:
                self.animation_phase = 0
                if event.type == pg.KEYUP:
                    self.jump = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.current_bug != 'Parasite':
                self.attack_leniency = 0

    def handle_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            if self.attacking <= 0:
                self.animation_type = s.Animation.WALK_LEFT
            self.acc.x = -s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            if self.attacking <= 0:
                self.animation_type = s.Animation.WALK_RIGHT
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
            if self.current_bug == 'Parasite':
                for enemy in self.game.special_enemies:
                    if self.pos.distance_squared_to(enemy.pos) < 100**2 and enemy.controllable:
                        self.current_bug = enemy.bug_type
                        self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
                        self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
                        self.stamina = self.max_stamina
                        self.animation_type = s.Animation.IDLE_RIGHT
                        self.image = self.game.all_images[self.current_bug][self.animation_type][0]
                        self.rect = self.image.get_rect()
                        self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
                        self.pos = enemy.pos
                        self.image = enemy.image
                        enemy.kill()
            else:
                SpecialEnemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
                self.current_bug = 'Parasite'
                self.animation_type = s.Animation.IDLE_RIGHT
                self.image = self.game.all_images[self.current_bug][self.animation_type][0]
                self.rect = self.image.get_rect()
                self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
                self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
                self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
                self.stamina = self.max_stamina

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

    def draw_ui(self):
        if self.max_stamina > 0:
            BAR_LENGTH = 100
            BAR_HEIGHT = 20
            percent = self.stamina / self.max_stamina
            fill = percent * BAR_LENGTH
            outline_rect = pg.Rect(0, 0, BAR_LENGTH, BAR_HEIGHT)
            fill_rect = pg.Rect(0, 0, fill, BAR_HEIGHT)
            if percent > 0.6:
                col = s.GREEN
            elif percent > 0.3:
                col = s.YELLOW
            else:
                col = s.RED
            pg.draw.rect(self.game.screen, col, fill_rect)
            pg.draw.rect(self.game.screen, s.BLACK, outline_rect, 2)

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

    def update(self):
        # temporary stamina drain, probably rework later
        if self.max_stamina > 0:
            self.stamina -= 0.1
        if self.stamina < 0:
            SpecialEnemy(self.game, self.pos.x, self.pos.y, self.current_bug, False)
            self.current_bug = 'Parasite'
            self.max_stamina = s.BUGS[self.current_bug]['MAX_STAMINA']
            self.animation_speed = s.BUGS[self.current_bug]['ANIMATION']
            self.stamina = self.max_stamina
            self.animation_type = s.Animation.IDLE_RIGHT
            self.image = self.game.all_images[self.current_bug][self.animation_type][0]
            self.rect = self.image.get_rect()
            self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
        # attacking countdown
        if self.attacking > 0:
            self.attacking -= 1
            if self.attacking <= 0:
                self.animation_type = self.direction
        if self.attack_leniency >= 0:
            self.attack_leniency += 1
        if 0 < self.attack_leniency <= 10 and not self.in_air:
            self.animation_phase = 0
            self.attacking = s.Attack_Properties[self.attack_facing]['DURATION']
            self.animation_type = s.Attack_Properties[self.attack_facing]['ANIMATION']
            self.animation_speed = s.Attack_Properties[self.attack_facing]['SPEED']
            self.attack_leniency = -1
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
        if self.attacking <= 0:
            if 0 < self.jump_leniency < 20 and self.in_air == False:
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
    def __init__(self, game, x, y, type):
        self.game = game
        self.groups = self.game.all_sprites, self.game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.attack_facing = s.Attacks.RIGHT_A
        self.animation_type = s.Animation.IDLE_RIGHT
        self.animation_phase = 0
        self.image = self.game.all_images[type][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = s.BUGS[type]['HIT_RECT']
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.next_animation_tick = 0
        self.animation_speed = s.BUGS[type]['ANIMATION']
        self.bug_type = type

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.bug_type][self.animation_type]):
            self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][self.animation_phase]
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed

    def update(self):
        self.animate_movement()


class SpecialEnemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, type, controllable=True):
        self.game = game
        self.groups = self.game.all_sprites, self.game.special_enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.attack_facing = s.Attacks.RIGHT_A
        self.animation_type = s.Animation.IDLE_RIGHT
        self.animation_phase = 0
        self.image = self.game.all_images[type][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = s.BUGS[type]['HIT_RECT']
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.bug_type = type
        self.controllable = controllable
        self.next_animation_tick = 0
        self.animation_speed = s.BUGS[self.bug_type]['ANIMATION']

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.animation_phase >= len(self.game.all_images[self.bug_type][self.animation_type]):
            self.animation_phase = 0
        self.image = self.game.all_images[self.bug_type][self.animation_type][self.animation_phase]
        self.animation_phase += 1
        self.next_animation_tick = pg.time.get_ticks() + self.animation_speed

    def update(self):
        self.animate_movement()
