import pygame as pg
import Settings as s
import Sprite as spr
from os import path
from Display import TiledMap, Camera, collide_hit_rect
vec = pg.math.Vector2


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        pg.font.init()
        self.screen = pg.display.set_mode(
            (s.WIDTH, s.HEIGHT), flags=pg.RESIZABLE | pg.SCALED | pg.SRCALPHA | pg.HWACCEL)
        self.clock = pg.time.Clock()
        # for debug
        self.debug_rects = []
        self.all_images = {}
        self.sound_cache = {}
        self.running = True
        self.load_data()

    def load_data(self):
        # load data needed at start
        self.game_folder = path.dirname(__file__)
        self.map_folder = path.join(self.game_folder, 'maps')
        self.img_folder = path.join(self.game_folder, 'img')
        self.sound_folder = path.join(self.game_folder, 'sounds')
        self.font = path.join(self.game_folder, 'font', 'techno_hideo.ttf')

    def load_map(self, map_name, playerLocation):
        # clear all groups
        self.all_sprites.empty()
        self.walls.empty()
        self.projectiles.empty()
        self.enemies.empty()
        self.semi_walls.empty()
        self.teleports.empty()
        self.pits.empty()
        self.player.add(self.all_sprites)
        # load a new map
        self.map = TiledMap(path.join(self.map_folder, map_name))
        self.camera = Camera(self.map.width, self.map.height)
        self.map_top_img, self.map_bottom_img = self.map.make_map()
        self.map_rect = self.map_bottom_img.get_rect()
        background = pg.image.load(path.join(self.img_folder, 'tree_background.png'))
        self.bgSurface = pg.Surface((self.map.width, self.map.height))
        for y in range(0, self.map.height, 512):
            for x in range(0, self.map.width, 768):
                self.bgSurface.blit(background, (x, y))
        if 'music' in self.map.tmxdata.properties and self.current_music != self.map.tmxdata.properties['music']:
            # Music Loading
            pg.mixer.music.fadeout(1000)
            self.current_music = self.map.tmxdata.properties['music']
            pg.mixer.music.load(path.join(self.sound_folder, self.map.tmxdata.properties['music']))
            pg.mixer.music.play(-1)
        # objects by id allows access to any object through id
        self.objects_by_id = {}
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == playerLocation:
                self.player.set_pos(obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                obstacle = spr.Obstacle(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, tile_object.properties['solid'])
                self.objects_by_id[tile_object.id] = obstacle
            if tile_object.name == 'pit':
                coord = self.map.tmxdata.get_object_by_id(tile_object.properties['destination'])
                dest = vec(coord.x, coord.y)
                pit = spr.Pit(
                    self, tile_object.x, tile_object.y, tile_object.width,
                    tile_object.height, dest)
                self.objects_by_id[tile_object.id] = pit
            if tile_object.type == 'mutated':
                enemy = spr.Enemy(
                    self, obj_center.x, obj_center.y, tile_object.name)
                self.objects_by_id[tile_object.id] = enemy
            if tile_object.name == 'turret':
                # self, game, health, damage, speed, target=None, die_on_impact=True
                health = tile_object.properties['health']
                damage = tile_object.properties['damage']
                try:
                    target = tile_object.properties['target']
                except KeyError:
                    target = self.player.pos
                speed = tile_object.properties['speed']
                die_on_impact = tile_object.properties['die']
                turret = spr.Turret(self, obj_center.x, obj_center.y, health, damage, speed, target, die_on_impact)
                self.objects_by_id[tile_object.id] = turret
            if tile_object.type == 'Teleport':
                spr.Teleport(
                    self, tile_object.x, tile_object.y,
                    tile_object.width, tile_object.height,
                    tile_object.name, tile_object.properties['playerLocation'])
            if tile_object.name == 'Arena':
                count = tile_object.properties['enemycount'].split(',')
                types = tile_object.properties['enemytypes'].split(';')
                locations = []
                for number in range(tile_object.properties['locations']):
                    name = 'location' + str(number)
                    location = self.map.tmxdata.get_object_by_id(tile_object.properties[name])
                    locations.append(vec(location.x, location.y))
                spr.Arena(self, tile_object.x, tile_object.y,
                          tile_object.width, tile_object.height,
                          tile_object.properties['waves'], count,
                          types, locations)

    def new(self):
        # start a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.semi_walls = pg.sprite.Group()
        self.teleports = pg.sprite.Group()
        self.pits = pg.sprite.Group()
        self.arena_enemies = pg.sprite.Group()
        for image in s.Loading:
            self.load_images(image)
        self.current_music = None
        self.player = spr.Player(self, 100, 100)
        self.load_map('test.tmx', 'player')
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
        hits = pg.sprite.spritecollide(self.player, self.projectiles, False, collide_hit_rect)
        for hit in hits:
            if not hit.friendly:
                self.player.hit(hit.damage)
                hit.hits -= 1
                if hit.hits <= 0:
                    hit.kill()
        hits = pg.sprite.spritecollide(self.player, self.pits, False, collide_hit_rect)
        for hit in hits:
            self.player.hit(s.PIT_DAMAGE)
            self.player.set_pos(hit.destination.x, hit.destination.y)
        hits = pg.sprite.spritecollide(self.player, self.teleports, False, collide_hit_rect)
        for hit in hits:
            self.load_map(hit.destination, hit.location)
            return

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # allow player class to run checks
            self.player.handle_events(event)
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_g:
                    self.debug_rects = []
            self.running = False

    def draw(self):
        # Game Loop - draw
        self.screen.blit(self.bgSurface, self.camera.apply_rect(self.map_rect, parallax=(6, 6)))
        self.screen.blit(self.map_bottom_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        self.screen.blit(self.map_top_img, self.camera.apply_rect(self.map_rect))
        self.player.draw_ui()
        # for debug purposes
        # surface = pg.Surface((self.player.hit_rect.width, self.player.hit_rect.height))
        # for rect in self.debug_rects:
        #     surface = pg.Surface((rect.width, rect.height))
        #     self.screen.blit(surface, self.camera.apply_rect(rect))
        # *after * drawing everything, flip the display
        pg.display.flip()

    def load_images(self, bug_name):
        if bug_name not in self.all_images:
            self.all_images[bug_name] = {}
            for direction in s.Animation:
                self.all_images[bug_name][direction] = []
                for i in [1, 2, 3, 4, 5, 6]:
                    mob_folder = path.join(self.img_folder, bug_name)
                    img = bug_name + direction.value + str(i) + ".png"
                    try:
                        loaded_image = pg.image.load(
                            path.join(mob_folder, img)).convert_alpha()
                        self.all_images[bug_name][direction].append(loaded_image)
                    except FileNotFoundError as e:
                        print("Mob image is missing", e)

    def get_sound(self, sound):
        if sound not in self.sound_cache:
            try:
                self.sound_cache[sound] = pg.mixer.Sound(path.join(self.sound_folder, sound))
            except FileNotFoundError:
                print("No sound file", sound)
                self.sound_cache[sound] = pg.mixer.Sound(path.join(self.sound_folder, "silence.mp3"))
        return self.sound_cache[sound]

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
