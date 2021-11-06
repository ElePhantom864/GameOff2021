# Sprite classes for platform game
import pygame as pg
import Settings as s
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((30, 40))
        self.image.fill(s.YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (s.WIDTH / 2, s.HEIGHT / 2)
        self.pos = vec(s.WIDTH / 2, s.HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.is_moving = False
        self.facing = s.Direction.DOWN
        self.jump = False
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

    def update(self):
        self.acc.x = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -s.PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = s.PLAYER_ACC
        if keys[pg.K_UP] or keys[pg.K_w]:
            if self.in_air == False:
                self.acc.y = s.PLAYER_JUMP_ACC
                self.in_air = True

        # apply gravity
        if self.in_air == True:
            self.acc.y += s.PLAYER_GRAVITY
            if self.acc.y >= s.PLAYER_MAX_FALL:
                self.acc.y = s.PLAYER_MAX_FALL
        # check if grounded
        if self.rect.bottom + self.vel.y + 0.5 * self.acc.y > s.HEIGHT - 10:
            self.acc.y = 0
            self.vel.y = 0
            self.rect.bottom = s.HEIGHT - 10
            self.in_air = False
        # apply friction
        self.acc.x += self.vel.x * s.PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > s.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = s.WIDTH

        self.rect.center = self.pos
