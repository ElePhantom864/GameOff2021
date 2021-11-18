import pygame as pg
from enum import Enum
vec = pg.math.Vector2


# For autocorrection
class Animation(Enum):
    WALK = 'Walk'
    IDLE = 'Idle'
    UP_A = 'UpA'
    DOWN_A = 'DownA'
    FRONT_A = 'FrontA'
    SPECIAL_A = 'SpecialA'
    HIT = 'Hit'
    PROJECTILE = 'Projectile'


# game options/settings
TITLE = "Project Parasite"
TILE_SIZE = 32
WIDTH = TILE_SIZE * 24
HEIGHT = TILE_SIZE * 16
FPS = 60


# Attack properties
Roach_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 30,
        'SPEED': 50,
        'HIT_RECT': pg.Rect(0, 0, 40, 10),
        'OFFSET': vec(25, 0),
        'DAMAGE': 50,
        'SOUND': 'RoachPunch'
    },
    Animation.DOWN_A: {
        'DURATION': 50,
        'SPEED': 60,
        'HIT_RECT': pg.Rect(0, 0, 40, 20),
        'OFFSET': vec(25, 30),
        'DAMAGE': 80,
        'SOUND': 'RoachPunch'
    },
    Animation.UP_A: {
        'DURATION': 20,
        'SPEED': 100,
        'HIT_RECT': pg.Rect(0, 0, 5, 40),
        'OFFSET': vec(15, -10),
        'DAMAGE': 10,
        'SOUND': 'RoachPunch'
    },
    Animation.SPECIAL_A: {
        'DURATION': 60,
        'SPEED': 100,
        'COST': 20,
        'DAMAGE': 100,
        'SOUND': 'RoachPunch'
    }
}

# General Properties
HEALTH = 1000
PLAYER_STUN = 30
PIT_DAMAGE = 100
BUGS = {
    'Parasite': {
        'ACC': 0.5,
        'JUMP_ACC': -3.5,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 22, 32),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 0,
        'ANIMATION': 150,
        'STUN': 100
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
        'ATTACKS': Roach_Attacks,
        'RECOVERY': 60,
        'STUN': 100,
        'HEALTH': 500
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
