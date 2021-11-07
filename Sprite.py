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
        self.attack_facing = s.Direction.NONE
        self.animation_type = s.Direction.WALK_RIGHT
        self.animation_phase = 0
        self.image = self.game.all_images[self.current_bug][self.animation_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
        self.hit_rect.center = self.rect.center
        self.jump = False
        self.jump_leniency = -1
        self.in_air = False
        self.next_animation_tick = 0

    def handle_events(self, event=pg.event.Event):
        # Only update variables if key pressed
        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            # Update movement
            if event.key in [pg.K_a, pg.K_d, pg.K_SPACE, pg.K_LEFT, pg.K_RIGHT] and event.type == pg.KEYDOWN:
                self.is_moving = True
            else:
                self.is_moving = False
            # Update direction
            self.attack_facing = s.Direction.NONE
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Direction.LEFT
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Direction.RIGHT
            if event.key == pg.K_UP or event.key == pg.K_w:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Direction.UP
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                if event.type == pg.KEYDOWN:
                    self.attack_facing = s.Direction.DOWN
            if event.key == pg.K_SPACE:
                self.animation_phase = 0
                if event.type == pg.KEYUP:
                    self.jump = False

    def animate_movement(self):
        if pg.time.get_ticks() < self.next_animation_tick:
            return
        if self.is_moving:
            self.image = self.game.all_images[self.current_bug][self.animation_type][self.animation_phase]
            self.animation_phase += 1
            if self.animation_phase >= len(self.game.all_images[self.current_bug][self.animation_type]):
                self.animation_phase = 0
            self.next_animation_tick = pg.time.get_ticks() + 100
        else:
            self.image = self.game.all_images[self.current_bug][self.animation_type][1]

    def update(self):
        self.acc.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.animation_type = s.Direction.WALK_LEFT
            self.acc.x = -s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.animation_type = s.Direction.WALK_RIGHT
            self.acc.x = s.BUGS[self.current_bug]['ACC']
        if keys[pg.K_SPACE]:
            if self.jump == False:
                self.jump_leniency = 0
                self.jump = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            if self.jump:
                self.pos.y += 5
                self.jump_leniency = -1
                self.jump = False
        if keys[pg.K_q]:
            for enemy in self.game.special_enemies:
                if self.pos.distance_squared_to(enemy.pos) < 100**2:
                    self.current_bug = enemy.bug_type
                    self.image = self.game.all_images[self.current_bug][self.animation_type][0]
                    self.rect = self.image.get_rect()
                    self.hit_rect = s.BUGS[self.current_bug]['HIT_RECT']
                    self.pos = enemy.pos
                    self.image = enemy.image
                    enemy.kill()
        # allow leniency for inputs
        if self.jump_leniency >= 0:
            self.jump_leniency += 1
        if 0 < self.jump_leniency < 20 and self.in_air == False:
            self.acc.y = s.BUGS[self.current_bug]['JUMP_ACC']
            self.in_air = True
        # apply gravity
        if self.in_air == True:
            self.acc.y += s.BUGS[self.current_bug]['GRAVITY']
            if self.acc.y >= s.BUGS[self.current_bug]['MAX_FALL']:
                self.acc.y = s.BUGS[self.current_bug]['MAX_FALL']
        # apply friction
        self.acc.x += self.vel.x * s.BUGS[self.current_bug]['FRICTION']
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
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
        if self.acc.y > 0:
            if collide_with_walls(self, self.game.semi_walls, 'y', False):
                self.acc.y = 0
                self.vel.y = 0
                self.in_air = False

        self.animate_movement()
        self.rect.center = self.pos


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


class SpecialEnemy(pg.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self.game = game
        self.groups = self.game.all_sprites, self.game.special_enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = self.game.all_images[type][s.Direction.WALK_RIGHT][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)
        self.bug_type = type
