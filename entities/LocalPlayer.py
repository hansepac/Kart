import numpy as np
from .Driver import Driver
from .Camera import Camera
from input import Controller
from utils.states import GameDebugState

class LocalPlayer(Driver):
    # it already has position and velocity stuff
    def __init__(self, mapmaster, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0]), windowsize = (400, 400)):
        super().__init__(mapmaster, pos = pos, direction_unitvec = direction_unitvec)
        self.controller: Controller = Controller()
        self.camera = Camera(*pos, np.atan2(direction_unitvec[2], direction_unitvec[0]), nx = windowsize[0], ny = windowsize[1])
        self.camera_height = 0.2
        self.camera_distance = 0.3
        self.camera_theta = 0.2
        self.gameDebugState: GameDebugState = GameDebugState(0)


    def updateCameraPositon(self):
        if self.gameDebugState != self.gameDebugState.FLY_DEBUG:
            # TODO: Adjust camera position factoring in the theta angle of ground
            self.camera.theta = self.camera_theta /2 -np.atan2(self.camera.y - self.pos[1], self.camera_distance) /2
            self.camera.phi = np.atan2(self.direction_unitvec[2], self.direction_unitvec[0]) + np.pi/2
            
            horizontal_unitvec = self.direction_unitvec/np.linalg.norm(self.direction_unitvec)
            horizontal_unitvec[1] = 0
            cam_pos = self.pos - self.camera_distance*horizontal_unitvec + np.array([0, 1, 0])*self.camera_height
            self.camera.x = cam_pos[0]
            self.camera.y = self.mapmaster.terrainGrid.get_ground_height(cam_pos) + self.camera_height
            self.camera.z = cam_pos[2]

    def updateCameraPositonOld(self):
        if self.gameDebugState != self.gameDebugState.FLY_DEBUG:
            #               TODO: Adjust camera position factoring in the theta angle of ground
            self.camera.theta = -np.atan2(self.camera_height, self.camera_distance)
            self.camera.phi = np.atan2(self.direction_unitvec[2], self.direction_unitvec[0]) + np.pi/2
            
            horizontal_unitvec = self.direction_unitvec/np.linalg.norm(self.direction_unitvec)
            horizontal_unitvec[1] = 0
            cam_pos = self.pos - self.camera_distance*horizontal_unitvec + np.array([0, 1, 0])*self.camera_height
            self.camera.x = cam_pos[0]
            self.camera.y = cam_pos[1]
            self.camera.z = cam_pos[2]


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


    

    