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
        self.image = pg.Surface((30, 40))
        self.image.fill(s.YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = s.PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.is_moving = False
        self.facing = s.Direction.DOWN
        self.jump = False
        self.jump_leniency = -1
        self.in_air = False

    def handle_events(self, event=pg.event.Event):
        # Only update variables if key pressed
        if event.type in [pg.KEYDOWN, pg.KEYUP]:
            # Update movement
            if event.type in [pg.K_w, pg.K_a, pg.K_d, pg.K_UP, pg.K_LEFT, pg.K_RIGHT]:
                self.is_moving = True
            else:
                self.is_moving = False
            # Update direction
            if event.key == pg.K_LEFT or event.key == pg.K_a:
                self.facing = s.Direction.LEFT
            if event.key == pg.K_RIGHT or event.key == pg.K_d:
                self.facing = s.Direction.RIGHT
            if event.key == pg.K_UP or event.key == pg.K_w:
                self.facing = s.Direction.UP
            if event.key == pg.K_DOWN or event.key == pg.K_s:
                self.facing = s.Direction.DOWN
            if event.key == pg.K_SPACE:
                if event.type == pg.KEYUP:
                    self.jump = False

    def update(self):
        self.acc.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -s.PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = s.PLAYER_ACC
        if keys[pg.K_SPACE]:
            if self.jump == False:
                self.jump_leniency = 0
                self.jump = True
        if keys[pg.K_q]:
            for enemy in self.game.enemies:
                if self.pos.distance_squared_to(enemy.pos) < 100**2:
                    self.pos = enemy.pos
                    self.image = enemy.image
                    enemy.kill()
        if self.jump_leniency >= 0:
            self.jump_leniency += 1
        if 0 < self.jump_leniency < 20 and self.in_air == False:
            self.acc.y = s.PLAYER_JUMP_ACC
            self.in_air = True
        # apply gravity
        if self.in_air == True:
            self.acc.y += s.PLAYER_GRAVITY
            if self.acc.y >= s.PLAYER_MAX_FALL:
                self.acc.y = s.PLAYER_MAX_FALL
        # apply friction
        self.acc.x += self.vel.x * s.PLAYER_FRICTION
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


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites, self.game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((30, 40))
        self.image.fill(s.RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)
