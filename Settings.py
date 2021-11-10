import pygame as pg
from enum import Enum


# For autocorrection
class Animation(Enum):
    WALK = 'Walk'
    IDLE = 'Idle'
    UP_A = 'UpA'
    DOWN_A = 'DownA'
    FRONT_A = 'FrontA'
    SPECIAL_A = 'SpecialA'


# game options/settings
TITLE = "Parasite Combat"
TILE_SIZE = 32
WIDTH = TILE_SIZE * 24
HEIGHT = TILE_SIZE * 16
FPS = 60

# Attack properties
Roach_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 30,
        'SPEED': 100
    },
    Animation.DOWN_A: {
        'DURATION': 30,
        'SPEED': 100
    },
    Animation.UP_A: {
        'DURATION': 30,
        'SPEED': 100
    },
    Animation.SPECIAL_A: {
        'DURATION': 60,
        'SPEED': 500,
        'COST': 20
    }
}

# Bug properties
BUGS = {
    'Parasite': {
        'ACC': 0.5,
        'JUMP_ACC': -3.5,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 20, 32),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 0,
        'ANIMATION': 150
    },
    'Roach': {
        'ACC': 0.4,
        'JUMP_ACC': -3.25,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 32, 64),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 100,
        'ANIMATION': 200,
        'ATTACKS': Roach_Attacks
    }
}

# things requiring load
Loading = ['Parasite', 'Roach']

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
