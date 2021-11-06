# Proof of Concept:
# Puzzle
import pygame as pg
import random

# game options/settings
TITLE = "FIGHT!"
WIDTH = 1500
HEIGHT = 1200
FPS = 60

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Sprite classes for platform game
vec = pg.math.Vector2


class Objects(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((100, 100))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.simplified = ['move_up', 'move_down', 'move_left']
        self.script = ['print("up")', 'print("down")', 'print("left")']
        self.cooldown = 0

    def update(self):
        self.cooldown += 1
        if self.cooldown > 60:
            exec(self.script[0])
            exec(self.script[1])
            exec(self.script[2])
            self.cooldown = 0

    def pressed(self):
        script1 = Script(self, 375, 900, 0)
        script2 = Script(self, 750, 900, 1)
        script3 = Script(self, 1125, 900, 2)
        self.game.objects.add(script1)
        self.game.objects.add(script2)
        self.game.objects.add(script3)
        self.game.all_sprites.add(script1)
        self.game.all_sprites.add(script2)
        self.game.all_sprites.add(script3)


class Script(pg.sprite.Sprite):
    def __init__(self, father, x, y, order):
        super().__init__()
        self.father = father
        self.image = pg.Surface((50, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = vec(x, y)
        self.order = order

    def pressed(self):
        self.father.simplified[self.order] = 'deleted'
        self.father.script[self.order] = 'print("deleted")'
        self.kill()


class Crosshair(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pg.Surface((10, 10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

    def shoot(self):
        hits = pg.sprite.spritecollide(self, self.game.objects, False)
        for hit in hits:
            hit.pressed()

    def update(self):
        self.rect.center = pg.mouse.get_pos()


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
        self.objects = pg.sprite.Group()
        self.crosshair = Crosshair(self)
        self.object = Objects(self)
        self.all_sprites.add(self.crosshair)
        self.all_sprites.add(self.object)
        self.objects.add(self.object)
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
            if event.type == pg.MOUSEBUTTONDOWN:
                self.crosshair.shoot()

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
pg.mouse.set_visible(False)
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
