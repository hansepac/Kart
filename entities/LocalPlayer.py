from numpy import array, sin, cos, pi
from .Driver import Driver
from .Camera import Camera
from input import Controller

class LocalPlayer(Driver):

    # it already has position and velocity stuff
    def __init__(self, x = 0, y = 0, z = 0, phi = 0):
        super().__init__(x, y, z, phi)
        self.controller: Controller = Controller()
        self.camera = Camera(x, y, z, phi)
        self.camera_height = 0.05
        self.camera_distance = 0.2
        self.camera_theta = 0.1

    def updateCameraPositon(self, win_x, win_y):
        # TODO: Adjust camera position factoring in the theta angle
        self.camera.nx = win_x
        self.camera.ny = win_y

        # update the camera position based on the player's position
        self.camera.x = self.pos[0] - sin(self.phi) * self.camera_distance
        self.camera.y = self.pos[1] + self.camera_height
        self.camera.z = self.pos[2] + cos(self.phi) * self.camera_distance
        self.camera.phi = self.phi

    def control(self):
        self.inputs = self.controller.get_input()


        
    # add stuff about getting controls


    

    