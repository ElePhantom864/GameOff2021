import pygame as pg
import Settings as s
import Sprite as spr
from os import path
from Display import TiledMap, Camera
vec = pg.math.Vector2


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode(
            (s.WIDTH, s.HEIGHT), flags=pg.RESIZABLE | pg.SCALED | pg.SRCALPHA | pg.HWACCEL)
        self.clock = pg.time.Clock()
        self.all_images = {}
        self.running = True
        self.load_data()

    def load_data(self):
        # load data needed at start
        self.game_folder = path.dirname(__file__)
        self.map_folder = path.join(self.game_folder, 'maps')
        self.img_folder = path.join(self.game_folder, 'img')

    def load_map(self, map_name):
        # load a new map
        self.map = TiledMap(path.join(self.map_folder, map_name))
        self.camera = Camera(self.map.width, self.map.height)
        self.map_top_img, self.map_bottom_img = self.map.make_map()
        self.map_rect = self.map_bottom_img.get_rect()

        # objects by id allows access to any object through id
        self.objects_by_id = {}
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'wall':
                obstacle = spr.Obstacle(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, tile_object.properties['solid'])
                self.objects_by_id[tile_object.id] = obstacle
            if tile_object.type == 'enemy':
                enemy = spr.Enemy(
                    self, obj_center.x, obj_center.y, tile_object.name)
                self.objects_by_id[tile_object.id] = enemy
            if tile_object.type == 'mutated':
                enemy = spr.SpecialEnemy(
                    self, obj_center.x, obj_center.y, tile_object.name)
                self.objects_by_id[tile_object.id] = enemy

    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.special_enemies = pg.sprite.Group()
        self.semi_walls = pg.sprite.Group()
        for image in s.Loading:
            self.load_images(image)
        self.load_map('Test.tmx')
        self.player = spr.Player(self, 100, 100)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(s.FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.camera.update(self.player)
        self.all_sprites.update()
        # hits = pg.sprite.spritecollide(self.player, self.projectiles, False)
        # # for hit in hits:
        # #     hit.kill()

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # allow player class to run checks
            self.player.handle_events(event)
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
            self.running = False

    def draw(self):
        # Game Loop - draw
        self.screen.blit(self.map_bottom_img, self.camera.apply_rect(self.map_rect))
        self.player.draw_ui()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            # if self.draw_debug:
            #     pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        self.screen.blit(self.map_top_img, self.camera.apply_rect(self.map_rect))
        # *after* drawing everything, flip the display
        pg.display.flip()

    def load_images(self, bug_name):
        if bug_name not in self.all_images:
            self.all_images[bug_name] = {}
            for direction in s.Animation:
                self.all_images[bug_name][direction] = []
                for i in [1, 2, 3, 4]:
                    mob_folder = path.join(self.img_folder, bug_name)
                    img = bug_name + direction.value + str(i) + ".png"
                    try:
                        loaded_image = pg.image.load(
                            path.join(mob_folder, img)).convert_alpha()
                        self.all_images[bug_name][direction].append(loaded_image)
                    except FileNotFoundError as e:
                        print("Mob image is missing", e)

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
