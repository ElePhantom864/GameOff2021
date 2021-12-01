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
        'SOUND': 'AddLater'
    },
    Animation.DOWN_A: {
        'DURATION': 50,
        'SPEED': 60,
        'HIT_RECT': pg.Rect(0, 0, 40, 20),
        'OFFSET': vec(25, 30),
        'DAMAGE': 80,
        'SOUND': 'AddLater'
    },
    Animation.UP_A: {
        'DURATION': 40,
        'SPEED': 100,
        'HIT_RECT': pg.Rect(0, 0, 5, 40),
        'OFFSET': vec(15, -10),
        'DAMAGE': 30,
        'SOUND': 'AddLater'
    },
    Animation.SPECIAL_A: {
        'DURATION': 60,
        'SPEED': 100,
        'COST': 40,
        'DAMAGE': 100,
        'SOUND': 'AddLater'
    }
}
Ant_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 60,
        'SPEED': 70,
        'HIT_RECT': pg.Rect(0, 0, 40, 10),
        'OFFSET': vec(25, 20),
        'DAMAGE': 70,
        'SOUND': 'AddLater'
    },
    Animation.DOWN_A: {
        'DURATION': 100,
        'SPEED': 120,
        'HIT_RECT': pg.Rect(0, 0, 40, 20),
        'OFFSET': vec(40, 30),
        'DAMAGE': 100,
        'SOUND': 'AddLater'
    },
    Animation.UP_A: {
        'DURATION': 160,
        'SPEED': 500,
        'HIT_RECT': pg.Rect(0, 0, 40, 5),
        'OFFSET': vec(30, -30),
        'DAMAGE': 150,
        'SOUND': 'AddLater'
    },
    Animation.SPECIAL_A: {
        'DURATION': 60,
        'SPEED': 100,
        'COST': 60,
        'DAMAGE': 25,
        'SOUND': 'AddLater'
    }
}
Bombardier_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 20,
        'SPEED': 100,
        'HIT_RECT': pg.Rect(0, 0, 50, 10),
        'OFFSET': vec(30, 0),
        'DAMAGE': 5,
        'SOUND': 'AddLater'
    },
    Animation.DOWN_A: {
        'DURATION': 60,
        'SPEED': 60,
        'HIT_RECT': pg.Rect(0, 0, 60, 10),
        'OFFSET': vec(0, 30),
        'DAMAGE': 70,
        'SOUND': 'AddLater'
    },
    Animation.UP_A: {
        'DURATION': 30,
        'SPEED': 50,
        'HIT_RECT': pg.Rect(0, 0, 5, 210),
        'OFFSET': vec(15, -70),
        'DAMAGE': 30,
        'SOUND': 'AddLater'
    },
    Animation.SPECIAL_A: {
        'DURATION': 60,
        'SPEED': 100,
        'COST': 50,
        'DAMAGE': 300,
        'SOUND': 'AddLater'
    }
}
Hercules_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 120,
        'SPEED': 100,
        'HIT_RECT': pg.Rect(0, 0, 50, 70),
        'OFFSET': vec(30, 0),
        'DAMAGE': 200,
        'SOUND': 'AddLater'
    },
    Animation.DOWN_A: {
        'DURATION': 60,
        'SPEED': 60,
        'HIT_RECT': pg.Rect(0, 0, 60, 10),
        'OFFSET': vec(0, 30),
        'DAMAGE': 80,
        'SOUND': 'AddLater'
    },
    Animation.UP_A: {
        'DURATION': 80,
        'SPEED': 50,
        'HIT_RECT': pg.Rect(0, 0, 5, 210),
        'OFFSET': vec(15, -70),
        'DAMAGE': 100,
        'SOUND': 'AddLater'
    },
    Animation.SPECIAL_A: {
        'DURATION': 100,
        'SPEED': 100,
        'COST': 80,
        'DAMAGE': 500,
        'SOUND': 'AddLater'
    }
}
Wasp_Attacks = {
    Animation.FRONT_A: {
        'DURATION': 30,
        'SPEED': 50,
        'HIT_RECT': pg.Rect(0, 0, 20, 10),
        'OFFSET': vec(45, 10),
        'DAMAGE': 50,
        'SOUND': 'AddLater'
    },
    Animation.DOWN_A: {
        'DURATION': 40,
        'SPEED': 60,
        'HIT_RECT': pg.Rect(0, 0, 40, 20),
        'OFFSET': vec(25, 30),
        'DAMAGE': 30,
        'SOUND': 'AddLater'
    },
    Animation.UP_A: {
        'DURATION': 30,
        'SPEED': 100,
        'HIT_RECT': pg.Rect(0, 0, 5, 40),
        'OFFSET': vec(25, -10),
        'DAMAGE': 20,
        'SOUND': 'AddLater'
    },
    Animation.SPECIAL_A: {
        'DURATION': 100,
        'SPEED': 100,
        'COST': 60,
        'DAMAGE': 100,
        'SOUND': 'AddLater'
    }
}
# General Properties
HEALTH = 1000
PLAYER_STUN = 30
PIT_DAMAGE = 50
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
        'ACC': 0.5,
        'JUMP_ACC': -3.25,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 32, 64),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 275,
        'ANIMATION': 200,
        'ATTACKS': Roach_Attacks,
        'RECOVERY': 60,
        'STUN': 100,
        'HEALTH': 300
    },
    'Ant': {
        'ACC': 0.45,
        'JUMP_ACC': -3.4,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 64, 64),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 150,
        'ANIMATION': 225,
        'ATTACKS': Ant_Attacks,
        'RECOVERY': 100,
        'STUN': 300,
        'HEALTH': 750
    },
    'Bombardier': {
        'ACC': 0.45,
        'JUMP_ACC': -3.5,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 45, 78),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 200,
        'ANIMATION': 100,
        'ATTACKS': Bombardier_Attacks,
        'RECOVERY': 75,
        'STUN': 250,
        'HEALTH': 750
    },
    'Hercules': {
        'ACC': 0.40,
        'JUMP_ACC': -3.4,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 48, 96),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 150,
        'ANIMATION': 250,
        'ATTACKS': Hercules_Attacks,
        'RECOVERY': 30,
        'STUN': 2000,
        'HEALTH': 1000
    },
    'Wasp': {
        'ACC': 0.575,
        'JUMP_ACC': -3.7,
        'GRAVITY': 0.5,
        'HIT_RECT': pg.Rect(0, 0, 56, 60),
        'MAX_FALL': 1.0,
        'FRICTION': -0.12,
        'MAX_STAMINA': 200,
        'ANIMATION': 100,
        'ATTACKS': Wasp_Attacks,
        'RECOVERY': 100,
        'STUN': 200,
        'HEALTH': 500
    }
}

# things requiring load
Loading = ['Parasite', 'Roach', 'Ant', 'Bombardier', 'Hercules', 'Wasp', 'Turret']

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
