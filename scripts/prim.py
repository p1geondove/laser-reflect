from math import atan2, pi, sin, cos
from abc import ABC

import pygame
from pygame import Vector2

from .const import EPSILON, GRAB_DIST, GRAB_DIST_SQ, COLOR_PRIM, MAX_DISTANCE
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

    def touch(self, pos:Vector2|tuple) -> bool:
        """returns True if a position is closer than GRAB_DIST to the objects stroke"""
        ...

class Line(Prim):
    def __init__(self, p1:Vector2|tuple, p2:Vector2|tuple) -> None:
        self.p1 = Vector2(p1)
        self.p2 = Vector2(p2)
        self.pressed = False
        self.pressed_a = False
        self.pressed_b = False
        self.hover = False
        self.hover_a = False
        self.hover_b = False

    def __repr__(self):
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.p1.x, self.p1.y, self.p2.x, self.p2.y)))
        return "Line("+vals+")"

    def draw(self, surface:pygame.Surface):
        pygame.draw.aaline(surface,COLOR_PRIM,self.p1,self.p2)

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed = self.hover
                self.pressed_a = self.hover_a
                self.pressed_b = self.hover_b

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed = False
                self.pressed_a = False
                self.pressed_b = False

        elif event.type == pygame.MOUSEMOTION:
            self.hover_a = self.p1.distance_squared_to(event.pos) < GRAB_DIST_SQ
            self.hover_b = self.p2.distance_squared_to(event.pos) < GRAB_DIST_SQ
            if not any((self.hover_a, self.hover_b)):
                self.hover = self.touch(event.pos)

            if self.pressed:
                self.p1 += event.rel
                self.p2 += event.rel
            elif self.pressed_a:
                self.p1 += event.rel
            elif self.pressed_b:
                self.p2 += event.rel

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        delta_points = self.p2 - self.p1
        denom = delta_points.cross(ray.dir)

        if abs(denom) < EPSILON:
            return

        delta_ray = ray.pos - self.p1
        t = delta_ray.cross(ray.dir) / denom
        s = delta_ray.cross(delta_points) / denom

        if t < EPSILON or t > 1 or s < EPSILON:
            return
        hit_pos = self.p1 + t * delta_points
        norm = Vector2(-delta_points.y, delta_points.x).normalize()
        dot = ray.dir.dot(norm)

        if dot > 0:
            norm = -norm
            dot = -dot

        refl_dir = ray.dir - 2 * dot * norm
        refl_ray = Ray(hit_pos, refl_dir)
        distance = s * ray.dir.length()

        return refl_ray, distance

    def touch(self, pos:Vector2|tuple) -> bool:
        pos = Vector2(pos)
        ab = self.p2 - self.p1
        ac = pos - self.p1
        dot = ac.dot(ab)
        ab_dist = ab.length_squared()
        t = dot / ab_dist if ab_dist else 0
        t = max(0, min(1, t))
        close = self.p1 + t * ab
        delta = pos - close
        return delta.length_squared() < GRAB_DIST_SQ

class Circle(Prim):
    def __init__(self, pos:Vector2|tuple, r:int|float) -> None:
        self.pos = Vector2(pos)
        self.radius = float(r)
        self.pressed_left = False
        self.pressed_right = False
        self.hover = False

    def __repr__(self) -> str:
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.pos.x, self.pos.y, self.radius)))
        return "Circle("+vals+")"

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.aacircle(surface, COLOR_PRIM, self.pos, self.radius, 1)

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.hover:
            if event.button == 1:
                self.pressed_left = True
            elif event.button == 3:
                self.pressed_right = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            if event.button == 3:
                self.pressed_right = False

        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.touch(event.pos)

            if self.pressed_left:
                self.pos += Vector2(event.rel)
            if self.pressed_right:
                self.radius = self.pos.distance_to(event.pos)

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        diff = ray.pos - self.pos
        a = 1
        b = 2 * diff.dot(ray.dir)
        c = diff.length_squared() - self.radius**2
        disc = b**2 - 4*a*c

        if disc < 0:
            return

        disc_sq:float = disc ** 0.5
        t1 = (-b - disc_sq) / (2 * a)
        t2 = (-b + disc_sq) / (2 * a)

        if t1 > EPSILON:
            t = t1
        elif t2 > EPSILON:
            t = t2
        else:
            return

        inter = ray.pos + ray.dir * t
        norm = inter - self.pos
        dot = ray.dir.dot(norm)
        mag = norm.length_squared()
        dir = ray.dir - 2 * (dot / mag) * norm

        return Ray(inter, dir), t

    def touch(self, pos:Vector2|tuple) -> bool:
        delta = Vector2(pos) - self.pos
        return abs(delta.length() - self.radius) < GRAB_DIST

class Ellipse(Prim):
    def __init__(self, pos:Vector2|tuple, radius:Vector2|tuple, angle:float|int) -> None:
        self.pos = Vector2(pos)
        self.radius = Vector2(radius)
        self.angle = float(angle)

        self.pressed_left = False
        self.pressed_right = False
        self.hover = False

    def draw(self, surface: pygame.Surface) -> None:
        points = []
        rot = Vector2(
            sin(self.angle),
            cos(self.angle)
        )

        for rad in (pi*2*(x/100) for x in range(101)):
            angle = Vector2(cos(rad), sin(rad))
            pos = self.radius.elementwise() * angle
            pos = Vector2(pos.cross(rot), pos.dot(rot)) + self.pos 
            points.append(pos)

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
                delta = Vector2(event.pos) - self.pos
                self.angle = delta.angle_rad
            elif self.pressed_left:
                self.pos += Vector2(event.rel)
            elif self.pressed_right:
                self.radius += Vector2(event.rel)
                if self.radius.x < 1:
                    self.radius.x = 1
                if self.radius.y < 1:
                    self.radius.y = 1

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        diff = ray.pos - self.pos

        rot = Vector2(
            sin(-self.angle),
            cos(-self.angle)
        )
        local_r = Vector2(
            diff.cross(rot),
            diff.dot(rot)
        )
        local_d = Vector2(
            ray.dir.cross(rot),
            ray.dir.dot(rot)
        )

        d = local_d.elementwise() / self.radius
        r = local_r.elementwise() / self.radius
        mul = local_r.elementwise() * local_d
        radius_sq = self.radius.elementwise() ** 2

        A = d.magnitude_squared()
        B = 2 * sum(mul.elementwise()/radius_sq)
        C = r.magnitude_squared() - 1

        disc = B**2 - 4*A*C

        if disc < 0:
            return None

        disc_sq:float = disc ** 0.5
        t1 = (-B - disc_sq) / (2 * A)
        t2 = (-B + disc_sq) / (2 * A)

        if t1 > EPSILON:
            t = t1
        elif t2 > EPSILON:
            t = t2
        else:
            return None

        inter_local = local_r + local_d * t
        norm_local = inter_local.elementwise() / self.radius.elementwise()**2
        refl_local = local_d.reflect(norm_local)

        rot = Vector2(sin(self.angle), cos(self.angle))
        inter = Vector2(
            inter_local.cross(rot),
            inter_local.dot(rot)
        ) + self.pos

        refl = Vector2(
            refl_local.cross(rot),
            refl_local.dot(rot)
        )

        refl_ray = Ray(inter, refl)

        return refl_ray, t

    def touch(self, pos:Vector2|tuple) -> bool:
        delta = Vector2(pos) - self.pos
        ang = Vector2(sin(-self.angle), cos(-self.angle))
        local = delta.reflect(ang)
        norm_dist = (local.elementwise() / self.radius).magnitude()

        if norm_dist < EPSILON:
            return False

        dist = abs(norm_dist-1) * min(self.radius)
        return dist < GRAB_DIST

class Bezier(Prim):
    def __init__(self, p1:Vector2|tuple, p2:Vector2|tuple, p3:Vector2|tuple, p4:Vector2|tuple) -> None:
        self.p1 = Vector2(p1)
        self.p2 = Vector2(p2)
        self.p3 = Vector2(p3)
        self.p4 = Vector2(p4)

        self.pressed_p1 = False
        self.pressed_p2 = False
        self.pressed_p3 = False
        self.pressed_p4 = False

        self.hover_p1 = False
        self.hover_p2 = False
        self.hover_p3 = False
        self.hover_p4 = False

        self.hover = False

        # these only update when any of the points move, so they get updated together with the points in handle_event
        self.calc_vecs()

    def draw(self, surface:pygame.Surface):
        points = []
        steps = 100
        for i in range(steps):
            t = i / (steps-1)
            p1 = self.v1 * t + self.p1
            p2 = self.v2 * t + self.p2
            p3 = self.v3 * t + self.p3
            v4 = p2 - p1
            v5 = p3 - p2
            p4 = v4 * t + p1
            p5 = v5 * t + p2
            v6 = p5 - p4
            points.append(v6 * t + p4)

        pygame.draw.aalines(surface, COLOR_PRIM, False, points)

        color_hover = "grey30"
        color_pressed = "darkred"
        points = [self.p1, self.p2, self.p3, self.p4]
        hovered = [self.hover_p1, self.hover_p2, self.hover_p3, self.hover_p4]
        pressed = [self.pressed_p1, self.pressed_p2, self.pressed_p3, self.pressed_p4]
        if any(hovered):
            for pos, hover, press in zip(points, hovered, pressed):
                color = color_pressed if press else color_hover
                pygame.draw.aacircle(surface, color, pos, 5)

    def calc_vecs(self):
        self.v1 = self.p2 - self.p1
        self.v2 = self.p3 - self.p2
        self.v3 = self.p4 - self.p3

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.pressed_p1 = self.hover_p1
            self.pressed_p2 = self.hover_p2
            self.pressed_p3 = self.hover_p3
            self.pressed_p4 = self.hover_p4

        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed_p1 = False
            self.pressed_p2 = False
            self.pressed_p3 = False
            self.pressed_p4 = False

        elif event.type == pygame.MOUSEMOTION:
            self.hover_p1 = self.p1.distance_to(event.pos) < GRAB_DIST
            self.hover_p2 = self.p2.distance_to(event.pos) < GRAB_DIST
            self.hover_p3 = self.p3.distance_to(event.pos) < GRAB_DIST
            self.hover_p4 = self.p4.distance_to(event.pos) < GRAB_DIST

            if self.pressed_p1:
                self.p1 += event.rel
                self.calc_vecs()
            elif self.pressed_p2:
                self.p2 += event.rel
                self.calc_vecs()
            elif self.pressed_p3:
                self.p3 += event.rel
                self.calc_vecs()
            elif self.pressed_p4:
                self.p4 += event.rel
                self.calc_vecs()

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        def point_at(t: float):
            t = max(0, min(1, t))
            p1 = self.v1 * t + self.p1
            p2 = self.v2 * t + self.p2
            p3 = self.v3 * t + self.p3
            v4 = p2 - p1
            v5 = p3 - p2
            p4 = v4 * t + p1
            p5 = v5 * t + p2
            v6 = p5 - p4
            return v6 * t + p4

        def derivative_at(t):
            t = max(0, min(1, t))
            mt = 1 - t
            d1 = 3 * mt**2 * self.v1
            d2 = 6 * mt * t * self.v2
            d3 = 3 * t**2 * self.v3
            return d1 + d2 + d3

        def tangent_at(t:float):
            deriv = derivative_at(t)
            if deriv.magnitude_squared() > 0:
                return deriv.normalize()
            return Vector2(1,0)

        def normal_at(t: float):
            tan = tangent_at(t)
            return Vector2(-tan.y, tan.x)

        # coarse search to find approximate intersection
        best_t = None
        best_dist = MAX_DISTANCE
        steps = 100

        for i in range(steps):
            t = i / (steps - 1)
            point = point_at(t)

            to_point = point - ray.pos
            along_ray = to_point.dot(ray.dir)

            if EPSILON < along_ray < MAX_DISTANCE:
                closest_on_ray = ray.pos + ray.dir * along_ray
                dist_to_ray = point.distance_to(closest_on_ray)

                if dist_to_ray < 10:
                    if along_ray < best_dist:
                        best_dist = along_ray
                        best_t = t

        if best_t is None:
            return None

        # Newton-Raphson refinement
        t = best_t
        for _ in range(10):
            point = point_at(t)
            diff = point - ray.pos
            f = diff.cross(ray.dir)

            if abs(f) < 0.01:
                break

            fp = derivative_at(t).cross(ray.dir)

            if abs(fp) < 0.001:
                break

            t_new = t - f / fp
            t = max(0, min(1, t_new))

        # Final validation
        point = point_at(t)
        to_point = point - ray.pos
        along_ray = to_point.dot(ray.dir)

        if along_ray > 0:
            closest_on_ray = ray.pos + ray.dir * along_ray

            if point.distance_to(closest_on_ray) < 1:
                reflected = ray.dir.reflect(normal_at(t))
                return Ray(point, reflected), along_ray

        return None

    def touch(self, pos: tuple[int, int]) -> bool:
        ...
