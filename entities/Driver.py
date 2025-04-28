from numpy import array, sin, cos, arctan, pi, sqrt
import pygame as pg

class Driver:
    # this is any racing character, AI or player
    def __init__(self, x = 0, y=0, z=0, phi=0, theta=0):
        self.pos = array([x, y, z], dtype=float)
        self.vel = array([0, 0, 0], dtype=float)
        self.acc = array([0, 0, 0], dtype=float)
        self.normal = array([0, 1, 0], dtype=float)
        self.phi = phi
        self.theta = theta
        self.top_speed = 0.01
        self.turn_speed = 0.05

        self.rank = 0

        self.inputs = {
            "gas": False,
            "brake": False,
            "reverse": False,
            "turn_dir": 0, # Value from -1 to 1. -1 is left, 1 is right (or anything in between) 
            "drift": False,
            "use_item": False
        }

    def control(self):
        return self.inputs

    # put position/velocity stuff here 
    
    # put sprite stuff here. 

    def get_homo_pos(self):
        return array([*self.pos, 1])

    def updatePosition(self):
        # Update theta based on the normal vector of the track
        self.theta = arctan(self.normal[1] / sqrt(self.normal[0]**2 + self.normal[2]**2)) + pi/2
        # Update phi based on turning
        self.phi += self.turn_speed * self.inputs["turn_dir"]
        # print(self.phi)

        # print(f"phi: {self.phi}, theta: {self.theta}")
        # print(f"sin(phi): {cos(self.phi)}, cos(theta): {cos(self.theta)}")
        # print(f"sin(phi): {sin(self.phi)}, cos(theta): {cos(self.theta)}")

        # Update position
        if self.inputs["gas"]:
            self.pos[0] += -sin(self.phi) * cos(self.theta) * self.top_speed
            self.pos[2] += cos(self.phi) * cos(self.theta) * self.top_speed
            self.pos[1] += sin(self.theta) * self.top_speed
        if self.inputs["reverse"]:
            self.pos[0] -= -sin(self.phi) * cos(self.theta) * self.top_speed
            self.pos[2] -= cos(self.phi) * cos(self.theta) * self.top_speed
            self.pos[1] -= sin(self.theta) * self.top_speed

        
    def returnCurrentSprite(self):
        pass
