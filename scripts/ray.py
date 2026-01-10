from pygame import Vector2

class Ray:
    def __init__(self, pos:Vector2|tuple, dir:Vector2|tuple):
        self.pos = Vector2(pos)
        self.dir = Vector2(dir)
        self.norm()

    def norm(self):
        if self.dir.magnitude_squared():
            self.dir.normalize_ip()
        else:
            self.dir = Vector2(1,0)
