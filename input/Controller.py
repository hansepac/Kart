import pygame as pg

class Controller():
    def __init__(self, is_controller: bool = False):
        self.is_controller = is_controller
        self.joystick = None
        self.gas = pg.K_w
        self.brake = pg.K_LCTRL
        self.reverse = pg.K_s
        self.left = pg.K_a
        self.right = pg.K_d
        self.drift = pg.K_LSHIFT
        self.use_item = pg.K_SPACE
        self.enable_debug_mode = pg.K_TAB
        self.debug_mode = False
        # Menuing Controls for joystics
        self.ll = False
        self.lr = False
        self.lu = False
        self.ld = False
        self.click = False
        self.back = False

    def connect_controller(self, c):
        # Get Unconnected Controllers:
        for connected_controllers in [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]:
            for controller_class in c.controllers:
                if controller_class.is_controller and controller_class.joystick is not None:
                    if connected_controllers.get_instance_id() == controller_class.joystick.get_instance_id():
                        continue
            self.joystick = connected_controllers
            # Update Controls
            self.gas = 0
            self.brake = 1
            self.reverse = 2
            self.turn_axis = 0
            self.left = 14
            self.right = 15
            self.drift = 4
            self.use_item = 5
            self.enable_debug_mode = 6
            # Boolean values for controller joysticks:
            self.l0 = 0
            self.l1 = 0
            self.r2 = 0
            self.r3 = 0
            break

    def switch_input_mode(self, c):
        self.is_controller = not self.is_controller
        if self.is_controller:
            self.connect_controller(c)
        if not self.is_controller or self.joystick is None:
            self.joystick = None
            self.gas = pg.K_w
            self.brake = pg.K_LCTRL
            self.reverse = pg.K_s
            self.left = pg.K_a
            self.right = pg.K_d
            self.drift = pg.K_LSHIFT
            self.use_item = pg.K_SPACE
            self.enable_debug_mode = pg.K_TAB

    def update_controller(self, c, thres=0.5):
        # Attempt to connect to controller if not connected
        if self.is_controller and self.joystick is None:
            self.connect_controller(c)

        # Init Menuing controls
        self.ll = False
        self.lr = False
        self.lu = False
        self.ld = False
        self.click = False
        self.back = False

        # Update KEYDOWN events
        for event in c.events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True
                if event.button == 3:
                    self.back = True
            if event.type == pg.KEYDOWN:
                if event.key == self.enable_debug_mode:
                    self.debug_mode = not self.debug_mode
                if event.key == self.gas:
                    self.lu = True
                if event.key == self.reverse:
                    self.ld = True
                if event.key == self.left:
                    self.ll = True
                if event.key == self.right:
                    self.lr = True
                if event.key == self.use_item:
                    self.click = True
                if event.key == self.brake:
                    self.back = True
            elif event.type == pg.JOYBUTTONDOWN:
                if event.button == self.enable_debug_mode:
                    self.debug_mode = not self.debug_mode
                if event.button == self.gas:
                    self.click = True
                if event.button == self.reverse or event.button == self.brake:
                    self.back = True

        if self.joystick is not None:
            # Menuing Controls for joysticks
            if self.l0 < -thres and self.joystick.get_axis(0) > -thres:
                self.ll = True
            elif self.l0 > thres and self.joystick.get_axis(0) < thres:
                self.lr = True
            elif self.l1 < -thres and self.joystick.get_axis(1) > -thres:
                self.lu = True
            elif self.l1 > thres and self.joystick.get_axis(1) < thres:
                self.ld = True

            self.l0 = self.joystick.get_axis(0)
            self.l1 = self.joystick.get_axis(1)

        if self.lu or self.ld or self.ll or self.lr:
            pg.mouse.set_visible(False)

    def get_input(self):
        if self.joystick:
            return {
                "gas": self.joystick.get_button(self.gas),
                "brake": self.joystick.get_button(self.brake),
                "reverse": self.joystick.get_button(self.reverse),
                "turn_dir": self.joystick.get_axis(self.turn_axis),
                "drift": self.joystick.get_button(self.drift),
                "use_item": self.joystick.get_button(self.use_item),
                "debug_mode": self.debug_mode
            }
        else:
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
