from numpy import array, sin, cos, tan, pi
import numpy as np
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


        self.camMat = None
        self.updateCamMat()
        
        # now make the viewport matrix. 
        self.vpMat = array([[self.nx/2, 0, 0, (self.nx-1)/2], 
                                [0, self.ny/2, 0, (self.ny-1)/2], 
                                [0, 0, 0.5, 0.5]])

    # helps make a perspective matrix
    def perspective_matrix(self, fov, aspect_ratio, near, far):
        f = 1 / tan(fov * pi/360)
        return array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])

    # updates the camMat based on position and angle
    def updateCamMat(self):
        # make initial camera matrix 
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
        
        perspectiveMatrix = self.perspective_matrix(70, self.nx/self.ny, 0.1, 1000 )
        self.camMat = perspectiveMatrix @ thetaMatrix @ phiMatrix @ translationMatrix

    # updates the vpMat based on screenSize (only run if screen size changes)
    def updateVpMat(self):
        '''Update the viewport matrix if the size of the camera window changed. '''
        self.vpMat = array([[self.nx/2, 0, 0, (self.nx-1)/2], 
                                [0, self.ny/2, 0, (self.ny-1)/2], 
                                [0, 0, 0.5, 0.5]])

    # takes in homogeneous coords and returns screen coords 
    def getScreenCoords(self, inputCoordinates):
        # take in a list of input vectors and return the corresponding screen vectors 
        step1 = array(inputCoordinates) @ self.camMat.T

        # check for culling
        mask = np.max(np.abs(step1[:, :3]), axis=1) > np.abs(step1[:, 3])
    
        # now scale each row 
        inverse = 1 / step1[:, 3]
        step2 = step1 * inverse[:, np.newaxis]

        # now apply viewport matrix 
        step3 = step2 @ self.vpMat.T 

        # now set to zero if it shouldn't be shown
        step3[mask, :] = 0

        return step3
    

    def drawTriangle(self, triangle_homo_coords):
        ''' Renders a triangle (list of three 4d points) and returns the list of screen points. 
        The returned list may have more than 3 points based on clipping. '''
        # first transform each of the original points
        step1 = array(triangle_homo_coords) @ self.camMat.T 

        # check for culling
        mask = np.max(np.abs(step1[:, :3]), axis=1) > np.abs(step1[:, 3])
        num_of_hidden = np.sum(mask)

        if num_of_hidden == 0:
            # Normal rendering
            # now scale each row 
            inverse = 1 / step1[:, 3]
            step2 = step1 * inverse[:, np.newaxis]

            # now apply viewport matrix 
            step3 = step2 @ self.vpMat.T 

            # now set to zero if it shouldn't be shown
            step3[mask, :] = 0

            return step3
        elif num_of_hidden == 1 or num_of_hidden == 2:
            # get screen triangle 
            inverse = 1 / step1[:, 3]
            step2 = step1 * inverse[:, np.newaxis]
            step3 = step2 @ self.vpMat.T 

            # apply clipping
            clipped_polygon_2d = suthHodgClip(step3[:, 0:2], np.array([[0, 0], [0, self.ny], [self.nx, self.ny], [self.nx, 0]]))
            new_z_column = np.full((clipped_polygon_2d.shape[0], 1), np.mean(step3[:, 2]))
            clipped_polygon_3d = np.hstack((clipped_polygon_2d, new_z_column))
            return clipped_polygon_3d

        else:
            # if all the points are off the screen
            return []


    def control(self, inputs):

        dx, dy = pg.mouse.get_rel()

        sensitivity = 0.002
        move_speed = 0.01

        # Mouse movement adjusts viewing angles
        self.phi   += dx * sensitivity   # yaw (left-right)
        self.theta += -dy * sensitivity   # pitch (up-down)

        # Optional: clamp theta to avoid flipping
        max_pitch = 1.5  # radians ~85 degrees
        self.theta = max(-max_pitch, min(max_pitch, self.theta))

        # Direction vector based on yaw (phi)
        dir_x = sin(self.phi)
        dir_z = -cos(self.phi)

        # Strafe vector (perpendicular)
        strafe_x = cos(self.phi)
        strafe_z = sin(self.phi)

        shift_multiplier = 3.5 if inputs["drift"] else 1

        # Turn left/right input
        self.x += strafe_x * move_speed * shift_multiplier * inputs["turn_dir"]
        self.z += strafe_z * move_speed * shift_multiplier * inputs["turn_dir"]

        # WASD movement
        if inputs["gas"]:
            self.x += dir_x * move_speed * shift_multiplier
            self.z += dir_z * move_speed * shift_multiplier
        if inputs["reverse"]:
            self.x -= dir_x * move_speed * shift_multiplier
            self.z -= dir_z * move_speed * shift_multiplier
        if inputs["use_item"]:
            self.y += move_speed * shift_multiplier
        if inputs["brake"]:
            self.y -= move_speed * shift_multiplier

            
        


#### Clipping tools
# Importing required libraries
import numpy as np

# Defining maximum number of points in polygon
MAX_POINTS = 20

# Function to return x-value of point of intersection of two lines
def x_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    num = (x1*y2 - y1*x2) * (x3-x4) - (x1-x2) * (x3*y4 - y3*x4)
    den = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
    return num/den

# Function to return y-value of point of intersection of two lines
def y_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    num = (x1*y2 - y1*x2) * (y3-y4) - (y1-y2) * (x3*y4 - y3*x4)
    den = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
    return num/den

# Function to clip all the edges w.r.t one clip edge of clipping area
def clip(poly_points, poly_size, x1, y1, x2, y2):
    new_points = np.zeros((MAX_POINTS, 2), dtype=int)
    new_poly_size = 0

    # (ix,iy),(kx,ky) are the co-ordinate values of the points
    for i in range(poly_size):
        # i and k form a line in polygon
        k = (i+1) % poly_size
        ix, iy = poly_points[i]
        kx, ky = poly_points[k]

        # Calculating position of first point w.r.t. clipper line
        i_pos = (x2-x1) * (iy-y1) - (y2-y1) * (ix-x1)

        # Calculating position of second point w.r.t. clipper line
        k_pos = (x2-x1) * (ky-y1) - (y2-y1) * (kx-x1)

        # Case 1 : When both points are inside
        if i_pos < 0 and k_pos < 0:
            # Only second point is added
            new_points[new_poly_size] = [kx, ky]
            new_poly_size += 1

        # Case 2: When only first point is outside
        elif i_pos >= 0 and k_pos < 0:
            # Point of intersection with edge and the second point is added
            new_points[new_poly_size] = [x_intersect(x1, y1, x2, y2, ix, iy, kx, ky),
                                         y_intersect(x1, y1, x2, y2, ix, iy, kx, ky)]
            new_poly_size += 1
            new_points[new_poly_size] = [kx, ky]
            new_poly_size += 1

        # Case 3: When only second point is outside
        elif i_pos < 0 and k_pos >= 0:
            # Only point of intersection with edge is added
            new_points[new_poly_size] = [x_intersect(x1, y1, x2, y2, ix, iy, kx, ky),
                                         y_intersect(x1, y1, x2, y2, ix, iy, kx, ky)]
            new_poly_size += 1

        # Case 4: When both points are outside
        else:
            pass  # No points are added, but we add a pass statement to avoid the IndentationError

    # Copying new points into a separate array and changing the no. of vertices
    clipped_poly_points = np.zeros((new_poly_size, 2), dtype=int)
    for i in range(new_poly_size):
        clipped_poly_points[i] = new_points[i]

    return clipped_poly_points, new_poly_size

# Function to implement Sutherland–Hodgman algorithm
def suthHodgClip(poly_points, clipper_points):
    poly_size = poly_points.shape[0]
    clipper_size = clipper_points.shape[0]

    new_poly_points, new_poly_size = poly_points.copy(), poly_size
    
    # i and k are two consecutive indexes
    for i in range(clipper_size):
        k = (i+1) % clipper_size

        # We pass the current array of vertices, it's size and the end points of the selected clipper line
        new_poly_points, new_poly_size = clip(new_poly_points, new_poly_size, clipper_points[i][0],
                                      clipper_points[i][1], clipper_points[k][0],
                                      clipper_points[k][1])

    
    
    return new_poly_points


