from math import atan2, pi, sin, cos
from abc import ABC

import pygame

from .const import EPSILON, GRAB_DIST, GRAB_DIST_SQ, COLOR_PRIM
from .ray import Ray

class Prim(ABC):
    def draw(self, surface:pygame.Surface) -> None:
        """drawing the thing onto a surface"""

    def handle_event(self, event:pygame.Event) -> None:
        """for making the thing interactive"""

    def reflect(self, ray:Ray) -> None | tuple[Ray, float]:
        """ 
            :param ray: Ray to test against
            :return None: Returns None if not intersecting
            :return Ray, float: Returns new Ray and distance if intersecting
        """
        ...

    def touch(self, pos:tuple[int,int]) -> bool:
        """returns True if a position is closer than GRAB_DIST to the objects stroke"""
        ...

class Line(Prim):
    def __init__(self, ax, ay, bx, by) -> None:
        self.ax = float(ax)
        self.ay = float(ay)
        self.bx = float(bx)
        self.by = float(by)
        self.pressed_a = False
        self.pressed_b = False

    def __repr__(self):
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.ax, self.ay, self.bx, self.by)))
        return "Line("+vals+")"

    def draw(self, surface:pygame.Surface):
        pygame.draw.aaline(surface,COLOR_PRIM,(self.ax, self.ay),(self.bx, self.by))

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed_a = (self.ax-event.pos[0])**2 + (self.ay-event.pos[1])**2 < GRAB_DIST_SQ
                self.pressed_b = (self.bx-event.pos[0])**2 + (self.by-event.pos[1])**2 < GRAB_DIST_SQ

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_a = False
                self.pressed_b = False

        elif event.type == pygame.MOUSEMOTION:
            if self.pressed_a:
                self.ax += event.rel[0]
                self.ay += event.rel[1]
            elif self.pressed_b:
                self.bx += event.rel[0]
                self.by += event.rel[1]

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        dx = self.bx - self.ax
        dy = self.by - self.ay
        denom = dx * ray.diry - dy * ray.dirx

        if abs(denom) < EPSILON:
            return

        dx_ray = ray.posx - self.ax
        dy_ray = ray.posy - self.ay
        t = (dx_ray * ray.diry - dy_ray * ray.dirx) / denom
        s = (dx_ray * dy - dy_ray * dx) / denom

        if t < EPSILON or t > 1 or s < EPSILON:
            return

        hit_x = self.ax + t * dx
        hit_y = self.ay + t * dy
        norm_x = -dy
        norm_y = dx
        norm_mag = (norm_x**2+norm_y**2)**0.5
        norm_x /= norm_mag
        norm_y /= norm_mag
        dot = ray.dirx * norm_x + ray.diry * norm_y

        if dot > 0:
            norm_x = -norm_x
            norm_y = -norm_y
            dot = -dot

        refl_dir_x = ray.dirx - 2 * dot * norm_x
        refl_dir_y = ray.diry - 2 * dot * norm_y
        refl_ray = Ray(hit_x, hit_y, refl_dir_x, refl_dir_y)
        distance = s * (ray.dirx**2 + ray.diry**2) ** 0.5

        return refl_ray, distance

    def touch(self, pos:tuple[int,int]) -> bool:
        posx, posy = pos
        abx = self.bx - self.ax
        aby = self.by - self.ay
        acx = posx - self.ax
        acy = posy - self.ay
        dot = acx * abx + acy * aby
        ab_dist = abx**2 + aby**2
        t = dot / ab_dist if ab_dist else 0
        t = max(0, min(1, t))
        closex = self.ax + t * abx
        closey = self.ay + t * aby
        dx = posx - closex
        dy = posy - closey
        return dx**2 + dy**2 < GRAB_DIST_SQ

class Circle(Prim):
    def __init__(self, px, py, r) -> None:
        self.posx = float(px)
        self.posy = float(py)
        self.radius = float(r)

        self.pressed_left = False
        self.pressed_right = False

    def __repr__(self) -> str:
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.posx, self.posy, self.radius)))
        return "Circle("+vals+")"

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.aacircle(surface,COLOR_PRIM,(self.posx,self.posy),self.radius,1)

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            dx = self.posx - event.pos[0]
            dy = self.posy - event.pos[1]
            pressed = bool(abs((dx**2 + dy**2)**0.5 - self.radius) < GRAB_DIST)
            if event.button == 1:
                self.pressed_left = pressed
            if event.button == 3:
                self.pressed_right = pressed
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            if event.button == 3:
                self.pressed_right = False
        if event.type == pygame.MOUSEMOTION:
            if self.pressed_left:
                self.posx += event.rel[0]
                self.posy += event.rel[1]
            if self.pressed_right:
                self.radius = ((self.posx-event.pos[0])**2+(self.posy-event.pos[1])**2)**0.5

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        diff_x = ray.posx - self.posx
        diff_y = ray.posy - self.posy
        a = ray.dirx ** 2 + ray.diry ** 2
        b = 2 * (diff_x * ray.dirx + diff_y * ray.diry)
        c = diff_x**2 + diff_y**2 - self.radius**2
        disc = b**2 - 4*a*c

        if disc < 0:
            return

        disc_sq = disc ** 0.5
        t1 = (-b - disc_sq) / (2 * a)
        t2 = (-b + disc_sq) / (2 * a)

        if t1 > EPSILON:
            t = t1
        elif t2 > EPSILON:
            t = t2
        else:
            return

        inter_x = ray.posx + ray.dirx * t
        inter_y = ray.posy + ray.diry * t
        norm_x = inter_x - self.posx
        norm_y = inter_y - self.posy
        dot = ray.dirx * norm_x + ray.diry * norm_y
        mag = norm_x**2 + norm_y**2
        dir_x = ray.dirx - 2 * (dot / mag) * norm_x
        dir_y = ray.diry - 2 * (dot / mag) * norm_y

        return Ray(inter_x, inter_y, dir_x, dir_y), t

    def touch(self, pos:tuple[int,int]) -> bool:
        posx, posy = pos
        dx = posx - self.posx
        dy = posy - self.posy
        dist = (dx**2 + dy**2)**0.5
        return abs(dist - self.radius) < GRAB_DIST

class Ellipse(Prim):
    def __init__(self, px, py, rx, ry, dir) -> None:
        self.px = float(px)
        self.py = float(py)
        self.rx = float(rx)
        self.ry = float(ry)
        self.dir = float(dir)

        self.pressed_left = False
        self.pressed_right = False

    def draw(self, surface: pygame.Surface) -> None:
        points = []

        for rad in (pi*2*(x/100) for x in range(101)):
            x = self.rx * cos(rad)
            y = self.ry * sin(rad)
            x2 = x * cos(self.dir) - y * sin(self.dir) + self.px
            y2 = x * sin(self.dir) + y * cos(self.dir) + self.py
            points.append((x2,y2))

        pygame.draw.aalines(surface, COLOR_PRIM, False, points)

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed_left = self.touch(event.pos)
            elif event.button == 3:
                self.pressed_right = self.touch(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            elif event.button == 3:
                self.pressed_right = False

        elif event.type == pygame.MOUSEMOTION:
            if self.pressed_left and self.pressed_right:
                dx = event.pos[0] - self.px
                dy = event.pos[1] - self.py
                self.dir = atan2(dy,dx)
            elif self.pressed_left:
                self.px += event.rel[0]
                self.py += event.rel[1]
            elif self.pressed_right:
                self.rx += event.rel[0]
                self.ry += event.rel[1]
                if self.rx == 0:
                    self.rx = 1
                if self.ry == 0:
                    self.ry = 1

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        """ I shamefully have to admit that this part was written by Claude.ai """
        # Transform ray to ellipse's local coordinate system
        # Translate to ellipse center
        ray_x = ray.posx - self.px
        ray_y = ray.posy - self.py
        
        # Rotate by -self.dir to align with ellipse axes
        cos_d = cos(-self.dir)
        sin_d = sin(-self.dir)
        local_rx = ray_x * cos_d - ray_y * sin_d
        local_ry = ray_x * sin_d + ray_y * cos_d
        local_dx = ray.dirx * cos_d - ray.diry * sin_d
        local_dy = ray.dirx * sin_d + ray.diry * cos_d
        
        # Solve quadratic: ray intersects ellipse when
        # ((rx + t*dx)/a)^2 + ((ry + t*dy)/b)^2 = 1
        # Rearranging: At^2 + Bt + C = 0
        A = (local_dx / self.rx)**2 + (local_dy / self.ry)**2
        B = 2 * (local_rx * local_dx / (self.rx**2) + local_ry * local_dy / (self.ry**2))
        C = (local_rx / self.rx)**2 + (local_ry / self.ry)**2 - 1
        
        disc = B**2 - 4*A*C
        
        if disc < 0:
            return None
        
        disc_sq = disc ** 0.5
        t1 = (-B - disc_sq) / (2 * A)
        t2 = (-B + disc_sq) / (2 * A)
        
        # Choose the first positive intersection
        if t1 > EPSILON:
            t = t1
        elif t2 > EPSILON:
            t = t2
        else:
            return None
        
        # Intersection point in local coordinates
        inter_local_x = local_rx + local_dx * t
        inter_local_y = local_ry + local_dy * t
        
        # Normal vector in local coordinates (gradient of ellipse equation)
        # For ellipse x^2/a^2 + y^2/b^2 = 1, gradient is (2x/a^2, 2y/b^2)
        norm_local_x = 2 * inter_local_x / (self.rx**2)
        norm_local_y = 2 * inter_local_y / (self.ry**2)
        
        # Normalize the normal vector
        norm_mag = (norm_local_x**2 + norm_local_y**2)**0.5
        norm_local_x /= norm_mag
        norm_local_y /= norm_mag
        
        # Reflect direction in local coordinates
        dot = local_dx * norm_local_x + local_dy * norm_local_y
        refl_local_dx = local_dx - 2 * dot * norm_local_x
        refl_local_dy = local_dy - 2 * dot * norm_local_y
        
        # Transform intersection point back to world coordinates
        cos_d = cos(self.dir)
        sin_d = sin(self.dir)
        inter_x = inter_local_x * cos_d - inter_local_y * sin_d + self.px
        inter_y = inter_local_x * sin_d + inter_local_y * cos_d + self.py
        
        # Transform reflected direction back to world coordinates
        refl_dx = refl_local_dx * cos_d - refl_local_dy * sin_d
        refl_dy = refl_local_dx * sin_d + refl_local_dy * cos_d
        
        refl_ray = Ray(inter_x, inter_y, refl_dx, refl_dy)
        
        return refl_ray, t

    def touch(self, pos:tuple[int,int]) -> bool:
        posx, posy = pos
        vx = posx - self.px
        vy = posy - self.py
        local_x = vx * cos(-self.dir) - vy * sin(-self.dir)
        local_y = vx * sin(-self.dir) + vy * cos(-self.dir)
        norm_dist = ((local_x/self.rx)**2 + (local_y/self.ry)**2)**0.5
        if norm_dist < EPSILON:
            return False

        pixel_dist = abs(norm_dist - 1) * min(self.rx, self.ry)
        return pixel_dist < GRAB_DIST

