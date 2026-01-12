from pygame import Vector2

class Ray:
    """ a line with with origin point and direction. Rays can be of infinite length in one direction """
    def __init__(self, pos:Vector2|tuple, angle:Vector2|tuple|float|int) -> None:
        self.pos = Vector2(pos)
        if isinstance(angle, Vector2|tuple):
            self.angle = Vector2(angle)
        elif isinstance(angle, int|float):
            self.angle = Vector2(1,0).rotate(angle)
        self.norm()

    def norm(self):
        """ always keep .angle normalized, it should be treated as a scalar, but Vector2 is used everywhere for performance reasons """
        if self.angle.magnitude_squared() > 0:
            self.angle.normalize_ip()
        else:
            self.angle = Vector2(1,0)

    def __repr__(self):
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.pos.x, self.pos.y, self.angle.x, self.angle.y)))
        return "Ray("+vals+")"
