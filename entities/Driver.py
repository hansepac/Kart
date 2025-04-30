import numpy as np
import pygame as pg

class Driver:
    # this is any racing character, AI or player
    def __init__(self, mapmaster, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0])):
        self.pos = pos
        self.vel_xz = 0
        self.vel_y = 0
        self.acc_y = 0
        self.omega = 0 # azimuthal velocity
        self.direction_unitvec = direction_unitvec
        self.rank = 0
        self.is_on_ground = True

        self.mapmaster = mapmaster

        # temporary
        self.normal = np.array([0, 1, 0])
        self.gas_force = 2 # actually this needs to depend on velocity or things blow up
        self.turn_speed = 0.08 # also should depend on speed
        self.slope_force = 0
        self.max_momentum = 1500
        self.dt = 1/30
        self.gravity = 10
        self.distance_to_ground_threshold = 0.01
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
    
    def get_speed(self, x, s = 0.4, r=0.2, a=0.005):
        # s = self.top_speed
        # r = self.reverse_top_speeed
        # a = self.acceleration_stat
        return (s+r)/(1+np.exp(-a*(x-np.log((s+r)/r-1)/a)))-r
    

    def get_homo_pos(self):
        return np.array([*self.pos, 1])

    def updatePosition(self):

        ground_height = self.mapmaster.terrainGrid.get_ground_height(self.pos)

        self.is_on_ground = self.pos[1] - ground_height < self.distance_to_ground_threshold

        #self.direction_unitvec*self.gas_force



        if self.is_on_ground:

            # Gas and Reverse
            if self.inputs["gas"]:
                if self.vel_xz < 0:
                    self.vel_xz *= 0.9
                self.vel_xz += self.gas_force
            if self.inputs["reverse"]:
                if self.vel_xz > 0:
                    self.vel_xz *= 0.9
                self.vel_xz -= self.gas_force




            vel_dependance = 2/(1+np.exp(-2*self.get_speed(self.vel_xz)))-1
            self.omega = -self.inputs["turn_dir"]*self.turn_speed*vel_dependance
            
            # now update unit direction vector from turning
            normal_vector = self.mapmaster.terrainGrid.get_normal_vector(self.pos) 
            self.direction_unitvec = rotation_matrix(normal_vector, self.omega) @ self.direction_unitvec

            # normal force 
            nf = normal_vector
            nf[1] = 0 # normal force only account for horizontal directions
            self.slope_force = 5*np.dot(nf, self.direction_unitvec)
            self.vel_xz += self.slope_force # this is the projection of the normal force on the direction vector
            
            # Friction and Brake
            if not self.inputs["gas"] and not self.inputs["reverse"]:
                self.vel_xz *= 0.95
            if self.inputs["brake"]:
                self.vel_xz *= 0.5
                # Full Stop
                if np.abs(self.vel_xz) < 0.1:
                    self.vel_xz = 0


        if self.pos[1] > ground_height:
            self.vel_y += -self.gravity * self.dt / 100
        else:
            self.vel_y = (self.pos[1] - ground_height)
            if self.vel_y < 0:
                self.vel_y = 0

        self.vel_xz = np.clip(self.vel_xz, -self.max_momentum, self.max_momentum)
        vel_final = self.direction_unitvec*self.get_speed(self.vel_xz)
        vel_final[1] = self.vel_y

        self.pos += vel_final * self.dt

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