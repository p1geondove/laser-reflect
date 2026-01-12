import pygame
from pygame import Vector2

from itertools import pairwise

from scripts.const import HEIGHT, WIDTH

from .ray import Ray
from .prim import Prim
from .const import *

class Laser:
    def __init__(self, pos:Vector2|tuple, dir:Vector2|tuple) -> None:
        #self.ray = Ray(pos, dir)
        self.pos = Vector2(pos)
        self.angle = Vector2(dir).normalize()
        self.points:list[Vector2] = [] # list of x,y intersection points
        self.hovered = False
        self.pressed_left = False
        self.pressed_right = False
        self.surface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)

    def trace(self, elements:list[Prim], max_bounce:int=MAX_BOUNCES, max_distance:int|float=MAX_DISTANCE):
        distance = 0
        ray = Ray(self.pos, self.angle)
        self.points = [self.pos]
        extend_end = True

        for _ in range(max_bounce):
            # call .reflect on each prim and filter out the ones that return None
            refs = list(filter(None, (e.reflect(ray) for e in elements)))
            # stop iterating if there arent any reflections
            if not refs: break
            # sort reflections by distance and pick the closest one
            ray, dist = sorted(refs, key=lambda x:x[1])[0]
            distance += dist
            self.points.append(ray.pos)

            if distance > max_distance:
                extend_end = False
                break
        else:
            extend_end = False

        # if there arent any reflections or we hit max_bounce, extend the last ray barely outside the screen
        if extend_end:
            self.points.append(ray.pos + ray.angle * (WIDTH+HEIGHT))

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                if event.button == 1:
                    self.pressed_left = True
                if event.button == 3:
                    self.pressed_right = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            elif event.button == 3:
                self.pressed_right = False

        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.pos.distance_squared_to(event.pos) < GRAB_DIST_SQ

            if self.pressed_left:
                self.pos += event.rel
            elif self.pressed_right:
                self.angle = Vector2(event.pos) - self.pos
                if self.angle.magnitude_squared():
                    self.angle.normalize_ip()
                else:
                    self.angle = Vector2(1,0)

    def draw(self, fancy=False):
        self.surface.fill(COLOR_BACKGROUND)
        if fancy:
            # blit every single line seperately with BLEND_RGB_ADD mode
            surf = pygame.Surface((WIDTH,HEIGHT))
            for p1, p2 in pairwise(self.points):
                br = pygame.draw.aaline(surf, COLOR_LASER_FANCY, p1, p2)
                self.surface.blit(surf, br.topleft, br, pygame.BLEND_RGB_ADD)
                surf.fill((0,0,0,0),br)
        else:
            # or just call aalines, wich doesnt care about alpha
            pygame.draw.aalines(self.surface, COLOR_LASER, False, self.points)

        # position dot
        pygame.draw.aacircle(self.surface, "red", self.pos, GRAB_DIST)

