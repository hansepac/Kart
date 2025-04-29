import numpy as np
import pygame as pg

class Driver:
    # this is any racing character, AI or player
    def __init__(self, mapmaster, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0])):
        self.pos = pos
        self.vel = np.array([0, 0, 0], dtype=float)
        self.acc = np.array([0, 0, 0], dtype=float)
        self.direction_unitvec = direction_unitvec
        self.rank = 0

        self.mapmaster = mapmaster

        # temporary
        self.normal = np.array([0, 1, 0])
        self.gas_force = 1 # actually this needs to depend on velocity or things blow up
        self.turn_speed = 0.08 # also should depend on speed
        self.dt = 1/30
        self.gravity = 10
        self.distance_to_ground_threshold = 0.0001
        self.mass = 1
        self.friction_coef = 0.3 # may depend on terrain


        self.inputs = {
            "gas": False,
            "brake": False,
            "reverse": False,
            "turn_dir": 0, # Value from -1 to 1. -1 is left, 1 is right (or anything in between) 
            "drift": False,
            "use_item": False
        }

    def disable_inputs(self):
        self.inputs = {
            "gas": False,
            "brake": False,
            "reverse": False,
            "turn_dir": 0, 
            "drift": False,
            "use_item": False
        }

    def control(self, events):
        return self.inputs
    

    def get_homo_pos(self):
        return np.array([*self.pos, 1])

    def updatePosition(self):
        # First take in inputs to define acceleration
        Force = np.zeros(3)

        if self.inputs["gas"]:
            Force += self.direction_unitvec*self.gas_force
        if self.inputs["reverse"]:
            Force += -self.direction_unitvec*self.gas_force

        # now update unit direction vector from turning
        normal_vector = self.mapmaster.terrainGrid.get_normal_vector(self.pos) 
        self.direction_unitvec = rotation_matrix(normal_vector, -self.turn_speed*self.inputs["turn_dir"]) @ self.direction_unitvec

        
        ground_height = self.mapmaster.terrainGrid.get_ground_height(self.pos)
        # pseudo vertical forces
        # nf = np.zeros(3)
        # if self.pos[1] - ground_height < self.distance_to_ground_threshold:
        #     # normal force 
        #     nf = normal_vector*self.gravity/normal_vector[1] # scale so it cancels gravity
        #     nf[1] = 0 # normal force only account for horizontal directions
        #     Force += nf*0.1
        # else:
        #     # gravity
        #     Force += np.array([0, -self.gravity, 0])
        
        # insert friction here 
        # Force += - self.vel/np.linalg.norm(self.vel)*np.linalg.norm(nf)*self.friction_coef # mu N in the - vhat direction



        # now update dynamics
        if not self.inputs["drift"]:
            # pseudo turning
            # if not drifting, just match direction vector (projective)
            self.direction_unitvec /= np.linalg.norm(self.direction_unitvec)
            self.vel = (self.vel @ self.direction_unitvec) * self.direction_unitvec

        self.acc = Force / self.mass
        self.vel += self.acc * self.dt 
        self.pos += self.vel * self.dt

        # clip ground if below
        if self.pos[1] < ground_height:
            self.pos[1] = ground_height

        
    def returnCurrentSprite(self):
        pass


def rotation_matrix(axis, theta):
    """
    Returns the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians (right-hand rule).
    
    axis: numpy array (3,)
    theta: float -- rotation angle in radians
    """
    axis = axis / np.linalg.norm(axis)
    kx, ky, kz = axis
    c = np.cos(theta)
    s = np.sin(theta)
    C = 1 - c
    
    R = np.array([
        [c + kx*kx*C,      kx*ky*C - kz*s,  kx*kz*C + ky*s],
        [ky*kx*C + kz*s,   c + ky*ky*C,     ky*kz*C - kx*s],
        [kz*kx*C - ky*s,   kz*ky*C + kx*s,  c + kz*kz*C    ]
    ])
    
    return R