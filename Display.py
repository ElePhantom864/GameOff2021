import pygame as pg
import pytmx
from Settings import WIDTH, HEIGHT
vec = pg.math.Vector2


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)


class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, top_surface, bottom_surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        tile = tile.convert_alpha()
                        if 'top' in layer.properties:
                            top_surface.blit(
                                tile, (x * self.tmxdata.tilewidth,
                                       y * self.tmxdata.tileheight))
                        else:
                            bottom_surface.blit(
                                tile, (x * self.tmxdata.tilewidth,
                                       y * self.tmxdata.tileheight))

    def make_map(self):
        top_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        bottom_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.render(top_surface, bottom_surface)
        return top_surface, bottom_surface


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect, parallax=(1, 1)):
        move_to = (self.camera.topleft[0] / parallax[0], self.camera.topleft[1] / parallax[1])
        return rect.move(move_to)

    def apply_point(self, point):
        return vec(point[0] - abs(self.camera.topleft[0]),
                   point[1] - abs(self.camera.topleft[1]))

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
