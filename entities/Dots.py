from __init__ import pg
from random import randint

class Dots():
    def __init__(self, x: int, y: int, z: int, color = (randint(100, 255), randint(100, 255), randint(100, 255))):
        self.x = x
        self.y = y
        self.color = color
        self.size = 5

    def draw(self, screen):
        pg.draw.circle(screen, self.color, (self.x, self.y), self.size)