import pygame as pg
from pygame import Vector2

class Player:
    def __init__(self, pos = Vector2(0,0)):
        self.pos = pos
        self.vel = Vector2(0,0)
        self.speed = 1
    
    def update(self):
        # Adjust velocity based on key presses
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel[0] -= self.speed
        if keys[pg.K_d]:
            self.vel[0] += self.speed
        if keys[pg.K_w]:
            self.vel[1] -= self.speed
        if keys[pg.K_s]:
            self.vel[1] += self.speed

        # Slow player if no keys are pressed
        if not keys[pg.K_a] and not keys[pg.K_d] and not keys[pg.K_w] and not keys[pg.K_s]:
            self.vel *= 0.9

        # Update position
        self.pos += self.vel

    def draw(self, window):
        pg.draw.circle(window, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 10)