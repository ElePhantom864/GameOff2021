import pygame as pg
from enum import Enum


# For autocorrection
class Animation(Enum):
    WALK_RIGHT = 'Right'
    WALK_LEFT = 'Left'
    IDLE_LEFT = 'LeftIdle'
    IDLE_RIGHT = 'RightIdle'


class Attacks(Enum):
    UP_A = 'UpA'
    DOWN_A = 'DownA'
    LEFT_A = 'LeftA'
    RIGHT_A = 'RightA'
    NONE = 'None'


# game options/settings
TITLE = "Parasite Combat"
TILE_SIZE = 32
WIDTH = TILE_SIZE * 24
HEIGHT = TILE_SIZE * 16
FPS = 60

# Player properties
BUGS = {
    'Parasite': {
        'ACC': 0.5,
        'JUMP_ACC': -4.0,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 20, 32),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 0,
    },
    'Mantis': {
        'ACC': 0.75,
        'JUMP_ACC': -4.0,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 32, 32),
        'MAX_FALL': 0.5,
        'FRICTION': -0.12,
        'MAX_STAMINA': 100
    }
}


# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
