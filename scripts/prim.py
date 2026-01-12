import math
from abc import ABC

import pygame
from pygame import Vector2

from .const import *
from .ray import Ray
from .ntimer import timer

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
        self.hovered = False
        self.hovered_a = False
        self.hovered_b = False

    def __repr__(self):
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.p1.x, self.p1.y, self.p2.x, self.p2.y)))
        return "Line("+vals+")"

    def draw(self, surface:pygame.Surface):
        for p, pr, hv in zip((self.p1, self.p2), (self.pressed_a, self.pressed_b), (self.hovered_a, self.hovered_b)):
            color = COLOR_PRIM_DRAGGED if pr else (COLOR_PRIM_HOVERED if hv else COLOR_PRIM)
            pygame.draw.aacircle(surface, color, p, GRAB_DIST)

        color = COLOR_PRIM_DRAGGED if self.pressed else (COLOR_PRIM_HOVERED if self.hovered else COLOR_PRIM)
        pygame.draw.aaline(surface, color, self.p1, self.p2)

    def handle_event(self, event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed = self.hovered
                self.pressed_a = self.hovered_a
                self.pressed_b = self.hovered_b

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed = False
                self.pressed_a = False
                self.pressed_b = False

        elif event.type == pygame.MOUSEMOTION:
            self.hovered_a = self.p1.distance_squared_to(event.pos) < GRAB_DIST_SQ
            self.hovered_b = self.p2.distance_squared_to(event.pos) < GRAB_DIST_SQ
            if not any((self.hovered_a, self.hovered_b)):
                self.hovered = self.touch(event.pos)

            if self.pressed:
                self.p1 += Vector2(event.rel)
                self.p2 += Vector2(event.rel)
            elif self.pressed_a:
                self.p1 += Vector2(event.rel)
            elif self.pressed_b:
                self.p2 += Vector2(event.rel)

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        delta_points = self.p2 - self.p1
        denom = delta_points.cross(ray.angle)

        if abs(denom) < EPSILON:
            return

        delta_ray = ray.pos - self.p1
        t = delta_ray.cross(ray.angle) / denom
        s = delta_ray.cross(delta_points) / denom

        if t < EPSILON or t > 1 or s < EPSILON:
            return
        hit_pos = self.p1 + t * delta_points
        norm = Vector2(-delta_points.y, delta_points.x).normalize()
        dot = ray.angle.dot(norm)

        if dot > 0:
            norm = -norm
            dot = -dot

        refl_dir = ray.angle - 2 * dot * norm
        refl_ray = Ray(hit_pos, refl_dir)
        distance = s * ray.angle.length()

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
        self.hovered = False

    def __repr__(self) -> str:
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.pos.x, self.pos.y, self.radius)))
        return "Circle("+vals+")"

    def draw(self, surface: pygame.Surface) -> None:
        color = COLOR_PRIM_DRAGGED if (self.pressed_left or self.pressed_right) else (COLOR_PRIM_HOVERED if self.hovered else COLOR_PRIM)
        pygame.draw.aacircle(surface, color, self.pos, self.radius, 1)

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
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
            self.hovered = self.touch(event.pos)

            if self.pressed_left:
                self.pos += Vector2(event.rel)
            if self.pressed_right:
                self.radius = self.pos.distance_to(event.pos)

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        diff = ray.pos - self.pos
        a = 1
        b = 2 * diff.dot(ray.angle)
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

        inter = ray.pos + ray.angle * t
        norm = inter - self.pos
        dot = ray.angle.dot(norm)
        mag = norm.length_squared()
        dir = ray.angle - 2 * (dot / mag) * norm

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
        self.hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        points = []
        rot = Vector2(
            math.sin(self.angle),
            math.cos(self.angle)
        )

        for rad in (math.pi*2*(x/100) for x in range(101)):
            angle = Vector2(math.cos(rad), math.sin(rad))
            pos = self.radius.elementwise() * angle
            pos = Vector2(pos.cross(rot), pos.dot(rot)) + self.pos 
            points.append(pos)
        color = COLOR_PRIM_DRAGGED if (self.pressed_left or self.pressed_right) else (COLOR_PRIM_HOVERED if self.hovered else COLOR_PRIM)
        pygame.draw.aalines(surface, color, False, points)

    def handle_event(self, event: pygame.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed_left = self.hovered
            elif event.button == 3:
                self.pressed_right = self.hovered

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            elif event.button == 3:
                self.pressed_right = False

        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.touch(event.pos)
            if self.pressed_left and self.pressed_right:
                delta = Vector2(event.pos) - self.pos
                self.angle = delta.angle_rad
            elif self.pressed_left:
                self.pos += Vector2(event.rel)
            elif self.pressed_right:
                self.radius += Vector2(event.rel)

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        diff = ray.pos - self.pos

        rot = Vector2(
            math.sin(-self.angle),
            math.cos(-self.angle)
        )
        local_r = Vector2(
            diff.cross(rot),
            diff.dot(rot)
        )
        local_d = Vector2(
            ray.angle.cross(rot),
            ray.angle.dot(rot)
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

        rot = Vector2(math.sin(self.angle), math.cos(self.angle))
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
        ang = Vector2(math.sin(-self.angle), math.cos(-self.angle))
        local = delta.reflect(ang)
        norm_dist = (local.elementwise() / self.radius).magnitude()

        if norm_dist < EPSILON:
            return False

        dist = abs(norm_dist-1) * min(self.radius)
        return dist < GRAB_DIST

class Bezier(Prim):
    def __init__(self, pos:list|tuple) -> None:
        self.pos = [Vector2(p) for p in pos]
        self.pressed = [False, False, False, False]
        self.hovered = [False, False, False, False]
        self.pressed_stroke = False
        self.hovered_stroke = False

    def point_at(self, t:float):
        # Using Bernstein basis for stability in point_at
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        return (self.pos[0] * mt3 + 
                self.pos[1] * (3 * mt2 * t) + 
                self.pos[2] * (3 * mt * t2) + 
                self.pos[3] * t3)

    def draw(self, surface: pygame.Surface):
        for a, b in zip(self.pos, self.pos[1:]):
            pygame.draw.aaline(surface, "grey20", a, b)

        points = [self.point_at(t / 99) for t in range(100)]
        color = COLOR_PRIM_DRAGGED if self.pressed_stroke else (COLOR_PRIM_HOVERED if self.hovered_stroke else COLOR_PRIM)
        pygame.draw.aalines(surface, color, False, points)

        for p, pr, hv in zip(self.pos, self.pressed, self.hovered):
            color = COLOR_PRIM_DRAGGED if pr else (COLOR_PRIM_HOVERED if hv else COLOR_PRIM)
            pygame.draw.circle(surface, color, p, GRAB_DIST)
    
    def handle_event(self, event: pygame.Event):
        if event.type == pygame.MOUSEMOTION:
            for i, p in enumerate(self.pos):
                self.hovered[i] = p.distance_to(event.pos) < GRAB_DIST
                if self.pressed[i]:
                    self.pos[i] += event.rel
            if not any(self.hovered):
                self.hovered_stroke = self.touch(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i, h in enumerate(self.hovered):
                if h:
                    self.pressed[i] = True
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressed = [False] * 4

    def normal_at(self, t: float):
        t = max(0, min(1, t))
        mt = 1 - t
        d1 = 3 * mt**2 * (self.pos[1]-self.pos[0])
        d2 = 6 * mt * t * (self.pos[2]-self.pos[1])
        d3 = 3 * t**2 * (self.pos[3]-self.pos[2])
        tan = Vector2(d1 + d2 + d3)
        if tan.magnitude_squared():
            tan.normalize_ip()
        else:
            tan = Vector2(1,0)
        return Vector2(-tan.y, tan.x)

    def reflect(self, ray: Ray) -> None | tuple[Ray, float]:
        """
        Finds the closest intersection point on the Bezier for the given Ray.
        Uses the implicit line equation of the ray to find roots.
        """
        # 1. Define Ray as an implicit line: Ax + By + C = 0
        # Normal to the ray direction is (-dy, dx)
        # A = -ray.angle.y, B = ray.angle.x
        # C = -(A*px + B*py)
        A = -ray.angle.y
        B = ray.angle.x
        C = -(A * ray.pos.x + B * ray.pos.y)

        # 2. Get Bezier coefficients for X(t) and Y(t)
        # Using the Bernstein form coefficients converted for the cubic power basis
        bx = [
            -self.pos[0].x + 3*self.pos[1].x - 3*self.pos[2].x + self.pos[3].x, # t^3
            3*self.pos[0].x - 6*self.pos[1].x + 3*self.pos[2].x,               # t^2
            -3*self.pos[0].x + 3*self.pos[1].x,                                # t
            self.pos[0].x                                                      # 1
        ]
        by = [
            -self.pos[0].y + 3*self.pos[1].y - 3*self.pos[2].y + self.pos[3].y, # t^3
            3*self.pos[0].y - 6*self.pos[1].y + 3*self.pos[2].y,               # t^2
            -3*self.pos[0].y + 3*self.pos[1].y,                                # t
            self.pos[0].y                                                      # 1
        ]

        # 3. Combine: P(t) = A*X(t) + B*Y(t) + C = 0
        poly = [
            A * bx[0] + B * by[0],
            A * bx[1] + B * by[1],
            A * bx[2] + B * by[2],
            A * bx[3] + B * by[3] + C
        ]

        # 4. Solve the cubic polynomial for t in [0, 1]
        # Using a condensed version of the analytical solver
        def get_roots(P):
            a, b, c, d = P
            if abs(a) < 1e-7: # Quadratic fallback
                if abs(b) < 1e-7: return [-d/c] if abs(c) > 1e-7 else []
                delta = c*c - 4*b*d
                if delta < 0: return []
                sd = math.sqrt(delta)
                return [(-c-sd)/(2*b), (-c+sd)/(2*b)]
            
            # Cubic roots
            A_c, B_c, C_c = b/a, c/a, d/a
            Q = (3*B_c - A_c**2) / 9
            R = (9*A_c*B_c - 27*C_c - 2*A_c**3) / 54
            D = Q**3 + R**2
            res = []
            if D >= 0:
                sd = math.sqrt(D)
                S = math.copysign(abs(R+sd)**(1/3), R+sd)
                T = math.copysign(abs(R-sd)**(1/3), R-sd)
                res.append(-A_c/3 + (S + T))
            else:
                th = math.acos(R / math.sqrt(-Q**3))
                mq = 2 * math.sqrt(-Q)
                res = [mq * math.cos(th/3) - A_c/3, 
                       mq * math.cos((th + 2*math.pi)/3) - A_c/3,
                       mq * math.cos((th + 4*math.pi)/3) - A_c/3]
            return [t for t in res if 0 <= t <= 1]

        t_values = get_roots(poly)
        if not t_values:
            return None

        # 5. Process hits and find the closest valid one
        hits = []
        for t in t_values:
            hit_pos = self.point_at(t)
            offset = hit_pos - ray.pos
            
            # Use .dot to ensure the intersection is in the direction of the ray
            # and .magnitude for distance
            if offset.dot(ray.angle) > 0.01: # Small epsilon to prevent self-intersection
                dist = offset.magnitude()
                hits.append((hit_pos, dist, t))

        if not hits:
            return None

        # Sort by distance to find the "first" hit
        hit_pos, dist, t_hit = min(hits, key=lambda x: x[1])

        # 6. Calculate Reflection Ray
        normal = self.normal_at(t_hit)
        
        # Ensure normal faces the incoming ray using .dot
        if normal.dot(ray.angle) > 0:
            normal *= -1
            
        # Use Vector2.reflect
        reflect_angle = ray.angle.reflect(normal)
        
        return Ray(hit_pos, reflect_angle), dist

    def touch(self, pos: Vector2 | tuple) -> bool:
        """ 
        Returns True if the distance from 'pos' to the curve is < GRAB_DIST.
        Approximates by checking segments and refining the closest one.
        """
        target = Vector2(pos)
        
        # 1. Coarse search: Find the closest point among a set of samples
        # 10-15 samples is usually plenty for a 'grab' check
        steps = 12
        min_dist_sq = float('inf')
        best_t = 0
        
        for i in range(steps + 1):
            t = i / steps
            p = self.point_at(t)
            # Use magnitude_squared for performance in the loop
            d_sq = target.distance_squared_to(p)
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                best_t = t
        
        # 2. Local Refinement (Simple 2-step Golden Section or similar)
        # We look around best_t to see if a slightly different t is closer
        precision = 1.0 / steps
        search_t = best_t
        for _ in range(2): # Two iterations is enough for mouse interaction
            precision /= 2
            t_low = max(0, search_t - precision)
            t_high = min(1, search_t + precision)
            
            p_low = self.point_at(t_low)
            p_high = self.point_at(t_high)
            
            d_low = target.distance_squared_to(p_low)
            d_high = target.distance_squared_to(p_high)
            
            if d_low < min_dist_sq:
                min_dist_sq = d_low
                search_t = t_low
            elif d_high < min_dist_sq:
                min_dist_sq = d_high
                search_t = t_high

        # 3. Final check against GRAB_DIST
        return min_dist_sq < GRAB_DIST_SQ