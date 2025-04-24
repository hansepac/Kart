from numpy import array

class Driver:
    # this is any racing character, AI or player
    def __init__(self, x = 0, y=0, z=0):
        self.pos = array([x, y, z])
        self.vel = array([0, 0, 0])
        self.acc = array([0, 0, 0])

        self.rank = 0

    # put position/velocity stuff here 
    
    # put sprite stuff here. 

    def updatePosition():
        # this is where the physics happens
        pass 

    def returnCurrentSprite():
        pass