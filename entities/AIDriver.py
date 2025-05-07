from entities.Driver import Driver
import numpy as np
from random import uniform

class AIDriver(Driver):
    def __init__(self, mapmaster, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0]), car_sprite = 0):
        super().__init__(mapmaster, pos = pos, direction_unitvec = direction_unitvec, car_sprite=car_sprite)
        self.is_AI = True
        self.noise_t = 0

        # personality factors
        self.no_gas_chance = uniform(0, 0.2)
        self.no_drift_chance = uniform(0, 0.4)
        self.turn_rate = uniform(1, 3)
        self.drift_threshold = uniform(0, 1)
        
    def control(self, events):
        ''' This function looks at the game state and figures out 
            what the player controls need to be for the ai. The AI plays the game 
            the same way the user does. It doesn't have access to modified physics. '''
        
        self.inputs["gas"] = not (uniform(0, 1) < self.no_gas_chance)

        # angle between player and next flag
        displacement_unit_vec = np.array([self.mapmaster.flags[self.flag_index][0], self.mapmaster.flags[self.flag_index][2]]) - np.array([self.pos[0], self.pos[2]])
        phi1 = np.atan2(self.direction_unitvec[2], self.direction_unitvec[0])
        phi2 = np.atan2(displacement_unit_vec[1], displacement_unit_vec[0])
        angle_between = (((phi2 - phi1 + np.pi) % (2*np.pi)) - np.pi)
        self.inputs["turn_dir"] = 2/(1 + np.exp(-self.turn_rate*angle_between)) - 1 

        self.inputs["drift"] = (abs(self.inputs["turn_dir"]) > self.drift_threshold) ^ (uniform(0, 1) < self.no_drift_chance)
        
