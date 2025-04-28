from numpy import array, sin, cos, pi
from .Driver import Driver
from .Camera import Camera
from input import Controller
from utils.states import GameDebugState

class LocalPlayer(Driver):
    # it already has position and velocity stuff
    def __init__(self, x = 0, y = 0, z = 0, phi = 0, windowsize = (400, 400)):
        super().__init__(x, y, z, phi)
        self.controller: Controller = Controller()
        self.camera = Camera(x, y, z, phi, nx = windowsize[0], ny = windowsize[1])
        self.camera_height = 0.05
        self.camera_distance = 0.2
        self.camera_theta = 0.1
        self.gameDebugState: GameDebugState = GameDebugState(0)


    def updateCameraPositon(self):
        if self.gameDebugState != self.gameDebugState.FLY_DEBUG:
            # TODO: Adjust camera position factoring in the theta angle
            self.camera.theta = self.camera_theta

            # update the camera position based on the player's position
            self.camera.x = self.pos[0] - sin(self.phi) * self.camera_distance
            self.camera.y = self.pos[1] + self.camera_height
            self.camera.z = self.pos[2] + cos(self.phi) * self.camera_distance
            self.camera.phi = self.phi

    def control(self, events):
        inputs = self.controller.get_input(events)
        if inputs["debug_mode"]:
            self.gameDebugState = GameDebugState((self.gameDebugState.value + 1) % 3)
            self.disable_inputs()
        if self.gameDebugState == self.gameDebugState.FLY_DEBUG:
            self.camera.control(inputs)
        else:
            self.inputs = inputs



        
    # add stuff about getting controls


    

    