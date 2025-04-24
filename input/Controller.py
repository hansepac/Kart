from __init__ import pg

class Keyboard():
    def __init__(self):
        self.pressed = pg.key.get_pressed()

    def update(self):
        self.pressed = pg.key.get_pressed()

class Controller():
    def __init__(self, keyboard: Keyboard):
        self.keyboard = keyboard
        self.forward = pg.K_w
        self.backward = pg.K_s
        self.left = pg.K_a
        self.right = pg.K_d
        self.drift = pg.K_LSHIFT
        self.use_item = pg.K_SPACE

    def get_input(self):
        return {
            "forward": self.keyboard.pressed[self.forward],
            "backward": self.keyboard.pressed[self.backward],
            "left": self.keyboard.pressed[self.left],
            "right": self.keyboard.pressed[self.right],
            "drift": self.keyboard.pressed[self.drift],
            "use_item": self.keyboard.pressed[self.use_item]
        }
