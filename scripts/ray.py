from math import sin, cos, atan2

class Ray:
    def __init__(self, *args):
        """"""
        # ray from ray
        if len(args) == 1 and isinstance(args[0], Ray):
            self.posx:float|int = args[0].posx
            self.posy:float|int = args[0].posy
            self.dirx:float|int = args[0].dirx
            self.diry:float|int = args[0].diry

        # posx, posy, dir_rad 
        elif len(args) == 3 and all(isinstance(arg, (int, float)) for arg in args):
            self.posx:float|int = args[0]
            self.posy:float|int = args[1]
            self.dirx:float|int = cos(args[2])
            self.diry:float|int = sin(args[2])

        # posx, posy, dirx, diry 
        elif len(args) == 4 and all(isinstance(arg, (int, float)) for arg in args):
            self.posx:float|int = args[0]
            self.posy:float|int = args[1]
            self.dirx:float|int = args[2]
            self.diry:float|int = args[3]

        else:
            raise NotImplementedError(f"Can't create Ray with {args}")

        self._norm()
        self._angle = atan2(self.diry, self.dirx)
        self._endx = self.posx + self.dirx
        self._endy = self.posy + self.diry

    def __repr__(self):
        fs = lambda x: str(int(x)) if abs(x-int(x))<0.005 else str(round(x,2))
        vals = ", ".join(map(fs, (self.posx, self.posy, self.dirx, self.diry)))
        return "Ray("+vals+")"

    def _norm(self):
        mag_sq = (self.dirx**2+self.diry**2)
        if mag_sq == 0:
            self.dirx = 1
            self.diry = 0
        elif mag_sq > 1:
            mag = mag_sq**0.5
            self.dirx /= mag 
            self.diry /= mag

    @property
    def angle(self):
        return atan2(self.diry, self.dirx)

    @angle.setter
    def angle(self, value):
        self._angle = float(value)
        self.dirx = cos(value)
        self.diry = sin(value)


    @property
    def endx(self):
        return self.posx + self.dirx

    @endx.setter
    def endx(self, value):
        self._endx = float(value)
        self.dirx = self._endx - self.posx
        self._norm()


    @property
    def endy(self):
        return self.posy + self.diry

    @endy.setter
    def endy(self, value):
        self._endy = float(value)
        self.diry = self._endy - self.posy
        self._norm()

