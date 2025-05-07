import numpy as np
import pygame as pg
from utils.misc import create_id

class Driver:
    # this is any racing character, AI or player
    def __init__(self, mapmaster, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0]), is_alien = False, car_sprite = 0):
        self.is_alien = is_alien
        self.id = create_id()
        self.pos = pos.copy()
        self.speed = 0
        self.vel_y = 0
        self.acc_y = 0
        self.omega = 0 # azimuthal velocity
        self.phi = 0
        self.direction_unitvec = direction_unitvec.copy()
        self.other_forces = np.zeros(3) # other forces acting on the car

        self.flag_index = 0 

        self.impact_dt = 0

        self.is_on_ground = True
        self.drift_time = 0
        self.drift_angle = 0
        self.drift_boost = 0.5
        self.drift_direction = 0
        self.drift_turn_speed_mult = 1.5
        self.drift_speed_mult = 0.6

        self.mapmaster = mapmaster

        terrainPos = pos.copy()
        terrainPos[1] = 0
        self.terrainDynamic = self.mapmaster.createTerrainDynamic(terrainPos)

        # TODO: clean out the old stuff here

        self.actual_speed = 0
        self.past_speeds = np.zeros(5)

        # temporary
        self.normal = np.array([0, 1, 0])
        self.gas_force = 2 # actually this needs to depend on velocity or things blow up
        self.turn_speed = 0.08 # also should depend on speed
        self.slope_speed = 0
        self.max_momentum = 800
        self.dt = 1/30
        self.gravity = 10
        self.distance_to_ground_threshold = 0.01
        self.mass = 1
        self.friction_coef = 0.3 # may depend on terrain

        self.car_sprite = car_sprite

        self.inputs = {
            "gas": False,
            "brake": False,
            "reverse": False,
            "turn_dir": 0, # Value from -1 to 1. -1 is left, 1 is right (or anything in between) 
            "drift": False,
            "use_item": False
        }

        # this is a crude way of doing on button down for sounds. 
        self.last_drift_state = False
        self.last_go_state = False

    def disable_inputs(self):
        self.inputs = {
            "gas": False,
            "brake": False,
            "reverse": False,
            "turn_dir": 0, 
            "drift": False,
            "use_item": False
        }

    def get_data(self):
        return {
            "id": self.id,
            "pos": self.pos.tolist(),
            "flag_index": self.flag_index,
            "direction_unitvec": self.direction_unitvec.tolist(),
            "is_on_ground": bool(self.is_on_ground),
        }
    
    def update_from_server(self, data_json):
        # update the driver from the server
        self.pos = np.array(data_json["pos"])
        self.flag_index = data_json["flag_index"]
        self.direction_unitvec = np.array(data_json["direction_unitvec"])
        self.is_on_ground = data_json["is_on_ground"]

    def control(self, events):
        return self.inputs
    
    def get_speed(self, x, s = 0.8, r=0.3, a=0.007):
        # s = self.top_speed
        # r = self.reverse_top_speeed
        # a = self.acceleration_stat
        return (s+r)/(1+np.exp(-a*(x-np.log((s+r)/r-1)/a)))-r
    
    def get_acc(self, x, s = 0.8, r=0.3, a=0.005):
        # s = self.top_speed
        # r = self.reverse_top_speeed
        # a = self.acceleration_stat
        # x = self.get_speed(x) - self.get_speed(self.max_momentum)
        mult = 30
        x = abs(self.get_speed(x, s=s, r=r, a=a))/s*mult
        return (self.get_speed(x, s*mult*2, r=30, a=0.2) - s*x)/mult/2
    

    def get_homo_pos(self):
        return np.array([*self.pos, 1]) + np.array([0, 0.01, 0, 0]) # make it slightly above the ground. 

    def updatePosition(self, dt_in):
        dt = 30*dt_in

        ground_height = self.terrainDynamic.get_ground_height(self.pos)

        impact = not self.is_on_ground and self.pos[1] - ground_height < self.distance_to_ground_threshold

        self.is_on_ground = self.pos[1] - ground_height < self.distance_to_ground_threshold

        if self.is_on_ground:
            # Calm other forces
            self.other_forces *= 0.95

            # Gas and Reverse
            if self.inputs["gas"]:
                if self.speed < 0:
                    # Gives more responsive gas after going reverse
                    self.speed *= 0.8
                    self.other_forces += self.direction_unitvec * dt / 200
                self.speed += (self.gas_force + np.clip(1000/abs(self.speed), 1, 30)) * dt * (1-self.inputs["drift"]/1.5)
            if self.inputs["reverse"]:
                self.speed -= (self.gas_force + np.clip(1000/abs(self.speed), 1, 30)) * dt


            # DRIFTING / TURNING
            if self.inputs["drift"] and (self.drift_direction != 0 or self.inputs["turn_dir"] != 0) and self.speed > 100:
                if self.drift_direction == 0:
                    self.drift_direction = np.sign(self.inputs["turn_dir"])
                # Turn
                self.drift_turn(self.turn_speed, dt)
            elif self.inputs["drift"] and self.speed < 100:
                    # Too slow, reset drift, no boost
                    self.reset_drift(boost = False)
            else:
                # Once drift has been released, reset drift
                if self.drift_direction != 0:
                    self.reset_drift(boost = True)
                self.omega = -self.inputs["turn_dir"]*self.turn_speed*self.get_acc(self.speed) * dt
            
            # Get direction vector
            self.direction_unitvec = rotation_matrix(np.array([0,1,0]), self.omega) @ self.direction_unitvec
            

            # GROUND FORCES
            normal_vector = self.terrainDynamic.get_normal_vector(self.pos)
            no_y_normal_vector = normal_vector.copy()
            no_y_normal_vector[1] = 0 # normal force only account for horizontal directions
            slope_dir = np.dot(no_y_normal_vector, self.direction_unitvec)

            if slope_dir == 0:
                self.slope_speed = 0
            else:
                self.slope_speed = (5*slope_dir)**2 * np.sign(slope_dir) * dt * 2
            self.speed += self.slope_speed# How slope effects speed
            slippy_constant = 0.05 # Increasing this ground more "slippery"
            self.other_forces += slippy_constant*self.get_speed(self.speed)**2*(no_y_normal_vector - np.dot(no_y_normal_vector, self.direction_unitvec) * self.direction_unitvec)

            # IMPACT IMPULSE
            if impact and self.impact_dt < 0:
                self.impact_dt = 1
                if self.vel_y < 0:
                    impact_effect = max(abs(self.vel_y)**0.5, 0.25)
                    self.other_forces += no_y_normal_vector*impact_effect
            else:
                self.impact_dt -= dt
            
            # Friction and Brake
            if not self.inputs["gas"] and not self.inputs["reverse"]:
                self.speed *= 0.99
            if self.inputs["brake"]:
                self.speed *= 0.95

        else:
            # IN AIR
            # DRIFTING / TURNING
            air_turn_speed = 0.01
            if self.inputs["drift"] and self.drift_direction != 0 and self.speed > 100:
                self.drift_turn(air_turn_speed, dt, add_time = True)
            else:
                # Once drift has been released, reset drift
                if self.drift_direction != 0:
                    self.reset_drift(boost = True)
                self.omega = -self.inputs["turn_dir"]*air_turn_speed*self.get_acc(self.speed) * dt

            # Get direction vector
            self.direction_unitvec = rotation_matrix(np.array([0,1,0]), self.omega) @ self.direction_unitvec
            
        # Needed for camera on local player (and probably other things in the future)
        self.phi = np.arctan2(self.direction_unitvec[2], self.direction_unitvec[0]) + np.pi/2


        # trees
        trees, _ = self.terrainDynamic.get_trees()
        for tree in trees:
            if np.linalg.norm(self.pos - tree[0:3]) < 0.1:
                self.pos -= self.direction_unitvec * 0.2
                self.speed = 0


        # If above ground, apply gravity
        if self.pos[1] > ground_height:
            self.vel_y += -self.gravity * dt / 30 / 10
        else:
            # If below ground, apply floaty force
            floaty_constant = 1
            self.vel_y += (ground_height - self.pos[1])*floaty_constant
            if self.vel_y < 0:
                self.vel_y = 0

        if self.inputs["drift"]:
            max_speed = self.drift_speed_mult * self.max_momentum
        else:
            max_speed = self.max_momentum
        self.speed = np.clip(self.speed, -max_speed, max_speed)
        vel_final = self.direction_unitvec*self.get_speed(self.speed) + self.other_forces
        vel_final[1] = self.vel_y
        self.pos += vel_final / 30
        self.past_speeds[:-1] = self.past_speeds[1:] # shift old values
        self.past_speeds[-1] = np.sqrt(vel_final[0]**2 + vel_final[2]**2)/dt/30
        self.actual_speed = np.mean(self.past_speeds)

        # clip ground if below
        if self.pos[1] < ground_height:
            self.pos[1] = ground_height

        

    def drift_turn(self, turn_speed, dt, add_time = True):
        modified_turn_dir = np.clip(self.inputs["turn_dir"] + self.drift_direction, min(self.drift_turn_speed_mult*self.drift_direction, 0.5*self.drift_direction), max(self.drift_turn_speed_mult*self.drift_direction, 0.5*self.drift_direction))
        self.omega = -(modified_turn_dir) * turn_speed * self.get_acc(self.speed) * dt
        # Add to drift time and angle
        if add_time:
            self.drift_time += dt
        self.drift_angle += abs(self.omega)

    def reset_drift(self, boost = False):
        if boost:
            self.drift_multiplier = np.clip(self.drift_time/100 + self.drift_angle, 0, 3)
            if self.drift_multiplier > 1:
                self.other_forces += self.direction_unitvec * self.drift_boost * self.drift_multiplier
        self.drift_time = 0
        self.drift_angle = 0
        self.drift_direction = 0



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