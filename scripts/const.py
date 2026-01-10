import pygame

WIDTH = 800
HEIGHT = 800

EPSILON = 1e-10
GRAB_DIST = 5
GRAB_DIST_SQ = GRAB_DIST ** 2

MAX_BOUNCES = 2**20
MAX_DISTANCE = 10**10

COLOR_BACKGROUND = pygame.Color("grey10")
COLOR_PRIM = pygame.Color("white")
COLOR_LASER = pygame.Color("white")
COLOR_LASER_FANCY = pygame.Color(10,10,10)
