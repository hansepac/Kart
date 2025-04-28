import pygame as pg

class Controller():
    def __init__(self, isController: bool = False):
        if isController:
            pass
        else:
            self.gas = pg.K_w
            self.brake = pg.K_LCTRL
            self.reverse = pg.K_s
            self.left = pg.K_a
            self.right = pg.K_d
            self.drift = pg.K_LSHIFT
            self.use_item = pg.K_SPACE
            self.enable_debug_mode = pg.K_TAB
            self.debug_mode = False

    def get_input(self, events):
        keys = pg.key.get_pressed()

        # If enable_debug_mode is pressed, toggle debug mode
        # If we used keys[], it would be pressed every frame
        # and would be impossible to toggle
        self.debug_mode = False
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == self.enable_debug_mode:
                    self.debug_mode = not self.debug_mode

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
            "use_item": keys[self.use_item],
            "debug_mode": self.debug_mode
        }
