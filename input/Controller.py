import pygame as pg

class Controller():
    def __init__(self):
        self.gas = pg.K_w
        self.brake = pg.K_LCTRL
        self.reverse = pg.K_s
        self.left = pg.K_a
        self.right = pg.K_d
        self.drift = pg.K_LSHIFT
        self.use_item = pg.K_SPACE

    def get_input(self):
        keys = pg.key.get_pressed()
        turn_dir = 0
        if keys[self.left]:
            turn_dir = -1
        elif keys[self.right]:
            turn_dir = 1
        return {
            "gas": keys[self.gas],
            "brake": keys[self.brake],
            "reverse": keys[self.reverse],
            "turn_dir": turn_dir,
            "drift": keys[self.drift],
            "use_item": keys[self.use_item]
        }
