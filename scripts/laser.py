import pygame

from itertools import pairwise

from scripts.const import HEIGHT, WIDTH

from .ray import Ray
from .prim import Prim
from .const import COLOR_BACKGROUND, GRAB_DIST, GRAB_DIST_SQ, COLOR_LASER, COLOR_LASER_FANCY

class Laser:
    def __init__(self, posx, posy, dirx, diry) -> None:
        self.ray = Ray(posx, posy, dirx, diry)
        self.points:list[tuple[float,float]] = [] # list of x,y intersection points
        self.pressed_left = False
        self.pressed_right = False
        self.surface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)

    def trace(self, elements:list[Prim], max_bounce:int=500, max_distance:int|float=100000):
        distance = 0
        ray = self.ray
        self.points = [(self.ray.posx, self.ray.posy)]
        extend_end = True

        for _ in range(max_bounce):
            # call .reflect on each prim and filter out the ones that return None
            refs = list(filter(lambda x:x, (e.reflect(ray) for e in elements)))
            # stop iterating if there arent any reflections
            if not refs: break
            # sort reflections by distance and pick the closest one
            ray, dist = sorted(refs, key=lambda x:x[1])[0]
            distance += dist
            self.points.append((ray.posx, ray.posy))

            if distance > max_distance:
                extend_end = False
                break
        else:
            extend_end = False

        # if there arent any reflections or we hit max_bounce, extend the last ray barely outside the screen
        if extend_end:
            end_x = ray.posx + ray.dirx * (WIDTH+HEIGHT)
            end_y = ray.posy + ray.diry * (WIDTH+HEIGHT)
            self.points.append((end_x, end_y))

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (self.ray.posx-event.pos[0])**2+(self.ray.posy-event.pos[1])**2 < GRAB_DIST_SQ:
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
            if self.pressed_left:
                self.ray.posx += event.rel[0]
                self.ray.posy += event.rel[1]
            elif self.pressed_right:
                self.ray.dirx = event.pos[0] - self.ray.posx
                self.ray.diry = event.pos[1] - self.ray.posy
                self.ray.norm()

    def draw(self, fancy=False):
        self.surface.fill(COLOR_BACKGROUND)
        if fancy:
            # create a seperate surface for every single line
            surfaces = []
            for (ax, ay), (bx, by) in pairwise(self.points):
                px = min(ax, bx)
                py = min(ay, by)
                dx = abs(ax - bx)+1 # please dont ask me about this off by one, i have no clue... and it hurts my soul sooo bad
                dy = abs(ay - by)+1
                surf = pygame.Surface((max(1, dx), max(1, dy)), pygame.SRCALPHA)
                local_ax = ax - px
                local_ay = ay - py
                local_bx = bx - px
                local_by = by - py
                pygame.draw.aaline(surf, COLOR_LASER_FANCY, (local_ax, local_ay), (local_bx, local_by))
                surfaces.append((surf, (px, py)))
            self.surface.blits(surfaces)
        else:
            # or just call aalines, wich doesnt care about alpha
            #surf = pygame.Surface(surface.size, pygame.SRCALPHA)
            pygame.draw.aalines(self.surface, COLOR_LASER, False, self.points)
            #self.surface.blit(surf)

        # position dot
        pygame.draw.aacircle(self.surface, "red", (self.ray.posx,self.ray.posy), GRAB_DIST)

