from numpy import array, sin, cos, tan, pi
import numpy as np
from __init__ import Keyboard
import pygame as pg

class Camera:
    def __init__(self, x = 0, y = 0, z = 0, theta = 0, phi=0, nx=400, ny=400):
    
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
                                   [0, 0, 1, -self.z],
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
        camMat, vpMat = self.getCombinedMatrix()

        # step 1 
        step1 = array(inputCoordinates) @ camMat.T

        # check for culling
        mask = np.max(np.abs(step1[:, :3]), axis=1) > np.abs(step1[:, 3])
    
        # now scale each row 
        inverse = 1 / step1[:, 3]
        step2 = step1 * inverse[:, np.newaxis]

        # now apply viewport matrix 
        step3 = step2 @ vpMat.T 

        # now set to zero if it shouldn't be shown
        step3[mask, :] = 0

        return step3
    

    # def prepDrawEdges(self, edges):
    #     # takes in a list of pairs of input vectors (homogeneous)
    #     camMat, vpMat = self.getCombinedMatrix()

    #     # Convert the list of pairs into a numpy array with shape (n, 2, 4), where n is the number of pairs
    #     edges_array = np.array(edges)  # Shape (n, 2, 4), each pair is (2, 4)

    #     # Step 1: Apply the camera matrix (camMat) to each of the two points in each pair
    #     step1 = edges_array @ camMat.T  # This results in (n, 2, 4) after applying the camera matrix

    #     # Step 2: Create the mask to handle culling based on the condition
    #     mask = np.max(np.abs(step1[:, :, :3]), axis=2) > np.abs(step1[:, :, 3])
    #     step1[mask, :, :] = 0  # Set points to zero where they shouldn't be shown

    #     # Step 3: Apply the viewport matrix after culling
    #     step2 = step1 @ vpMat.T  # Apply the viewport matrix to the remaining points

    #     return step2
            
    
    def control(self, keyboard: Keyboard):
        dx, dy = pg.mouse.get_rel()

        sensitivity = 0.002
        move_speed = 0.01

        # Mouse movement adjusts viewing angles
        self.phi   += dx * sensitivity   # yaw (left-right)
        self.theta += -dy * sensitivity   # pitch (up-down)

        # Optional: clamp theta to avoid flipping
        max_pitch = 1.5  # radians ~85 degrees
        self.theta = max(-max_pitch, min(max_pitch, self.theta))

        keys = keyboard.pressed

        # Direction vector based on yaw (phi)
        dir_x = sin(self.phi)
        dir_z = -cos(self.phi)

        # Strafe vector (perpendicular)
        strafe_x = cos(self.phi)
        strafe_z = sin(self.phi)

        shift_multiplier = 3.5 if keys[pg.K_LSHIFT] else 1

        # WASD movement
        if keys[pg.K_w]:
            self.x += dir_x * move_speed * shift_multiplier
            self.z += dir_z * move_speed * shift_multiplier
        if keys[pg.K_s]:
            self.x -= dir_x * move_speed * shift_multiplier
            self.z -= dir_z * move_speed * shift_multiplier
        if keys[pg.K_a]:
            self.x -= strafe_x * move_speed * shift_multiplier
            self.z -= strafe_z * move_speed * shift_multiplier
        if keys[pg.K_d]:
            self.x += strafe_x * move_speed * shift_multiplier
            self.z += strafe_z * move_speed * shift_multiplier
        if keys[pg.K_SPACE]:
            self.y += move_speed * shift_multiplier
        if keys[pg.K_LCTRL]:
            self.y -= move_speed * shift_multiplier

            
        


