from numpy import array, sin, cos, tan, pi
from __init__ import Keyboard
import pygame as pg

class Camera:
    def __init__(self, x = 0, y = 0, z = 0, theta = pi/2, phi=0, nx=400, ny=400):
    
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.phi = phi

        # camera canvas coordinates. 
        self.nx = nx 
        self.ny = ny

    def perspective_matrix(self, fov, aspect_ratio, near, far):
        f = 1 / tan(fov * pi/360)
        return array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])


    def getCombinedMatrix(self):
        translationMatrix = array([[1, 0, 0, -self.x],
                                   [0, -1, 0, self.y],
                                   [0, 0, 1, self.z],
                                   [0, 0, 0, 1]])
        # the y axis gets flipped because y is up
        phiMatrix = array([[cos(self.phi), 0, sin(self.phi), 0],
                           [0, 1, 0, 0],
                           [-sin(self.phi), 0, cos(self.phi), 0], 
                           [0, 0, 0, 1]])
        thetaMatrix = array([[1, 0, 0, 0],
                             [0, cos(self.theta), -sin(self.theta), 0],
                             [0, sin(self.theta), cos(self.theta), 0],
                             [0, 0, 0, 1]])
        cameraMatrix = thetaMatrix @ phiMatrix @ translationMatrix

        # now make the projection matrix
        projectionMatrix = self.perspective_matrix(70, self.nx/self.ny, 0.1, 1000 )
        
        # now make the viewport matrix. 
        viewportMatrix = array([[self.nx/2, 0, 0, (self.nx-1)/2], 
                                [0, self.ny/2, 0, (self.ny-1)/2], 
                                [0, 0, 0.5, 0.5]])

        return projectionMatrix @ cameraMatrix, viewportMatrix

    # Improvement: replace for loop with array slicing
    def getScreenCoords(self, inputCoordinates):
        # take in a list of input vectors and return the corresponding screen vectors 
        newVectors = inputCoordinates
        camMat, vpMat = self.getCombinedMatrix()
        for i in range(len(inputCoordinates)):
            # first project the coordinate onto the screen
            step1 = camMat @ inputCoordinates[i] 
            # filter objects here 
            if step1[0] > -step1[3] and step1[0] < step1[3] and step1[1] > -step1[3] and step1[1] < step1[3] and step1[2] > -step1[3] and step1[2] < step1[3]:
                # now scale it so that the first entry is one
                step2 = step1/step1[3] # this step has to happen each time because the scalar might be different each time. 
                # now apply the viewport matrix 
                step3 = vpMat @ step2
                newVectors[i] = step3
            else:
                newVectors[i] = None
        return newVectors
    
    def control(self, keyboard: Keyboard):
        self.v = 3
        keys = keyboard.pressed
        if keys[pg.K_a]:
            self.phi += 0.05
        if keys[pg.K_d]:
            self.phi -= 0.05
        if keys[pg.K_w]:
            v = 1
            self.z -= cos(self.phi) * v
            self.x += sin(self.phi) * v
        if keys[pg.K_s]:
            v = -1
            self.z -= cos(self.phi) * v
            self.x += sin(self.phi) * v
        
    


