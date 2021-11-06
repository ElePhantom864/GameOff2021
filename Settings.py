import pygame as pg
from enum import Enum


# For autocorrection
class Direction(Enum):
    UP = 'Up'
    DOWN = 'Down'
    LEFT = 'Left'
    RIGHT = 'Right'


# game options/settings
TITLE = "Parasite Combat"
TILE_SIZE = 32
WIDTH = TILE_SIZE * 24
HEIGHT = TILE_SIZE * 16
FPS = 60

# Player properties
PLAYER_ACC = 0.5
PLAYER_JUMP_ACC = -4.0
PLAYER_GRAVITY = 0.5
PLAYER_HIT_RECT = pg.Rect(0, 0, 30, 40)
PLAYER_MAX_FALL = 1.0
PLAYER_FRICTION = -0.12

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
