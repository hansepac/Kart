import numpy as np
from noise import pnoise2

class Terrain:
    def __init__(self, grid_spacing = 1, nx = 100, nz = 100, center = np.array([0, 0, 0])):

        self.points = np.zeros((nx, nz, 3))
        self.homo_points = np.zeros((nx, nz, 4))
        self.grid_spacing = grid_spacing
        self.center = center
        self.nx, self.nz = nx, nz

        # every even row is off by a shift of (sqrt(3)/2 * grid_spacing) in j

        # generate perlin height
        for i in range(nx):
            for j in range(nz):
                self.points[j, i, 0] = (i + 3**0.5/2 * (j % 2) - nx/2)*grid_spacing + center[0]
                self.points[j, i, 1] = (j - nz/2)*grid_spacing + center[2]
                self.points[j, i, 2] = pnoise2((i + 3**0.5/2 * (j % 2)) / grid_spacing, j / grid_spacing)

                self.homo_points[j, i, 0] = (i + 3**0.5/2 * (j % 2) - nx/2)*grid_spacing + center[0]
                self.homo_points[j, i, 1] = (j - nz/2)*grid_spacing + center[2]
                self.homo_points[j, i, 2] = pnoise2((i + 3**0.5/2 * (j % 2)) / grid_spacing, j / grid_spacing)
                self.homo_points[j, i, 3] = 1
                
        # pack homogeneous triangles
        homo_triangles = []
        for i in range(self.nx - 1):
            for j in range(self.nz - 1):
                triangle = [self.homo_points[j, i, :], self.homo_points[j, i+1, :], self.homo_points[j+1, i, :]]
                homo_triangles.append(triangle)
                triangle = [self.homo_points[j, i+1, :], self.homo_points[j+1, i, :], self.homo_points[j+1, i+1, :]]
                homo_triangles.append(triangle)
        self.homo_triangles = homo_triangles


                
