# Proof of Concept:
# Platformer
import pygame as pg
import random

# game options/settings
TITLE = "Jumpy!"
WIDTH = 1500
HEIGHT = 1200
FPS = 60

# Player properties
PLAYER_ACC = 0.75
JUMP_ACC = -2
PLAYER_FRICTION = -0.06

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Classes for platform game
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((20, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(40, HEIGHT - 40)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.jump = False
        self.jumpCount = 0
        self.slideCount = 0

    def update(self):
        self.acc = vec(0, 0)
        if self.slideCount < 0:
            self.image = pg.Surface((20, 40))
            self.image.fill(YELLOW)
            self.rect = self.image.get_rect()
            self.slideCount += 0.05
        if self.pos.y < HEIGHT - 40:
            self.pos.y += 5
        if self.jumpCount > 10:
            self.jump = True
            self.jumpCount = -70
        if self.jumpCount < 0:
            self.jumpCount += 1
        else:
            self.jump = False
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        if keys[pg.K_UP] and not self.jump:
            self.jumpCount += 1
            self.acc.y = JUMP_ACC
        if keys[pg.K_DOWN]:
            self.image = pg.Surface((20, 10))
            self.image.fill(YELLOW)
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x, self.pos.y + 0)
            self.acc.x *= 2 + self.slideCount
            if self.slideCount > -2:
                self.slideCount -= 0.1
        # apply friction
        self.acc += self.vel * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        if self.pos.y > HEIGHT:
            self.pos.y = 0
        if self.pos.y < 0:
            self.pos.y = HEIGHT

        self.rect.center = self.pos


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True

    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        pass

    def show_go_screen(self):
        # game over/continue
        pass


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
