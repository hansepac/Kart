from __init__ import pg
from random import randint
from numpy import array

class Dots():
    def __init__(self, x: int, y: int, z: int):
        self.pos = array([x, y, z])
        self.color = (randint(100, 255), randint(100, 255), randint(100, 255))
        self.size = 5

    def get_pos(self):
        return array([*self.pos, 1])

    def draw(self, screen, win_x, win_y):
        pg.draw.circle(screen, self.color, (win_x, win_y), self.size)