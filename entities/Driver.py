from numpy import array

class Driver:
    # this is any racing character, AI or player
    def __init__(self, x = 0, y=0, z=0):
        self.pos = array([x, y, z])
        self.vel = array([0, 0, 0])
        self.acc = array([0, 0, 0])
        self.turn_angle = 0
        self.turn_speed = 0.01

        self.rank = 0

        self.inputs = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "drift": False,
            "use_item": False
        }

    # put position/velocity stuff here 
    
    # put sprite stuff here. 

    def updatePosition(self):
        if self.inputs["forward"]:
            self.vel[0] += 1

    def returnCurrentSprite(self):
        pass