from numpy import array, sin, cos, pi

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
        left, right, bottom, top, near, far = -3, 3, -3, 3, 5, 20
        projectionMatrix = array([[2*near/(right-left), 0, (right+left)/(right-left), 0],
                                [0, 2*near/(top-bottom), (top + bottom)/(top-bottom), 0], 
                                [0, 0, -1*(far + near)/(far - near), -2*far*near/(far-near)],
                                [0, 0, -1, 0]])
        
        # now make the viewport matrix. 
        viewportMatrix = array([[self.nx/2, 0, 0, (self.nx-1)/2], 
                                [0, self.ny/2, 0, (self.ny-1)/2], 
                                [0, 0, 0.5, 0.5]])

        return projectionMatrix @ cameraMatrix, viewportMatrix

    def getScreenCoords(self, inputCoordinates):
        # take in a list of input vectors and return the corresponding screen vectors 
        newVectors = inputCoordinates
        camMat, vpMat = self.getCombinedMatrix()
        for i in range(len(inputCoordinates)):
            # first project the coordinate onto the screen
            step1 = camMat @ inputCoordinates[i] 
            # now scale it so that the first entry is one
            step2 = step1/step1[3]
            # now apply the viewport matrix 
            step3 = vpMat @ step2
            newVectors[i] = step3