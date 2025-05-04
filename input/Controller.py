import pygame as pg

class Controller():
    def __init__(self, is_controller: bool = False):
        self.is_controller = is_controller
        self.joystick = None
        if is_controller and pg.joystick.get_count() > 0:
            print(pg.joystick.get_init(), pg.joystick.get_count())
            self.joystick = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())][0]
            self.gas = 1
            self.brake = 2
            self.reverse = 3
            self.turn_axis = 0
            self.drift = 4
            self.use_item = 5
            self.enable_debug_mode = 6
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
        self.debug_mode = False
        # If enable_debug_mode is pressed, toggle debug mode
        # If we used keys[], it would be pressed every frame
        # and would be impossible to toggle
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == self.enable_debug_mode:
                    self.debug_mode = not self.debug_mode
            elif event.type == pg.JOYBUTTONDOWN:
                if event.button == self.enable_debug_mode:
                    self.debug_mode = not self.debug_mode

        print(self.joystick, pg.joystick.get_count())

        if self.is_controller and self.joystick is None and pg.joystick.get_init() and pg.joystick.get_count() > 0:
            self.joystick = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())][0]
            self.gas = 1
            self.brake = 2
            self.reverse = 3
            self.turn_axis = 0
            self.drift = 4
            self.use_item = 5
            self.enable_debug_mode = 6

        if not self.is_controller or self.joystick is None:
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
                "use_item": keys[self.use_item],
                "debug_mode": self.debug_mode
            }
        else:
            return {
                "gas": self.joystick.get_button(self.gas),
                "brake": self.joystick.get_button(self.brake),
                "reverse": self.joystick.get_button(self.reverse),
                "turn_dir": self.joystick.get_axis(self.turn_axis),
                "drift": self.joystick.get_button(self.drift),
                "use_item": self.joystick.get_button(self.use_item),
                "debug_mode": self.debug_mode
            }
