class Ray:
    def __init__(self, posx, posy, dirx, diry):
        self.posx = float(posx)
        self.posy = float(posy)
        self.dirx = float(dirx)
        self.diry = float(diry)
        self.norm()

    def norm(self):
        mag_sq = (self.dirx**2+self.diry**2)
        if mag_sq == 0:
            self.dirx = 1
            self.diry = 0
        elif mag_sq > 1:
            mag = mag_sq**0.5
            self.dirx /= mag
            self.diry /= mag

