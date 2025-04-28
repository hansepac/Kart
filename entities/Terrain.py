import numpy as np
from noise import pnoise2

class Terrain:
    def __init__(self, grid_spacing = 1, noise_density = 1, noise_height= 1, nx = 100, nz = 100, center = np.array([0, 0, 0])):

        self.points = np.zeros((nx, nz, 3))
        self.homo_points = np.zeros((nx, nz, 4))
        self.grid_spacing = grid_spacing
        self.center = center
        self.nx, self.nz = nx, nz

        # every even row is off by a shift of (sqrt(3)/2 * grid_spacing) in j

        # generate perlin height
        for i in range(nx):
            for j in range(nz):
                self.points[j, i, 0] = (i + 0.5 * (j % 2) - nx/2)*grid_spacing + center[0]
                self.points[j, i, 2] = (j - nz/2)*grid_spacing*(3**0.5/2) + center[2]
                self.points[j, i, 1] = noise_height* pnoise2((i + 0.5 * (j % 2)) * noise_density, j * noise_density)

                self.homo_points[j, i, 0:3] = self.points[j, i, :]
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

    def get_ground_height(self, pos_3d):
        return bilinear_interpolate(self.points, pos_3d[0], pos_3d[2])
    
    
# for getting ground height
def bilinear_interpolate(tensor, x_target, z_target):
    # Get the shape of the tensor (n x m x 3)
    n, m, _ = tensor.shape
    
    # Extract the grid of x and z values (ignoring y for now)
    x_vals = tensor[:, :, 0]
    z_vals = tensor[:, :, 2]
    
    # Find the indices of the nearest x and z grid points
    i_x = np.searchsorted(x_vals[0, :], x_target)
    i_z = np.searchsorted(z_vals[:, 0], z_target)
    
    # Handle edge cases where the target is exactly on a grid point
    if i_x == 0:
        i_x = 0
    elif i_x == m:
        i_x = m - 1
    
    if i_z == 0:
        i_z = 0
    elif i_z == n:
        i_z = n - 1
    
    # Get the four nearest neighbors
    x0, x1 = x_vals[i_z, i_x], x_vals[i_z, min(i_x + 1, m - 1)]
    z0, z1 = z_vals[min(i_z + 1, n - 1), i_x], z_vals[i_z, i_x]
    
    y00, y01 = tensor[i_z, i_x, 1], tensor[i_z, min(i_x + 1, m - 1), 1]
    y10, y11 = tensor[min(i_z + 1, n - 1), i_x, 1], tensor[min(i_z + 1, n - 1), min(i_x + 1, m - 1), 1]

    # Interpolate in the x direction
    interp_x0 = y00 + (x_target - x0) * (y10 - y00) / (x1 - x0)
    interp_x1 = y01 + (x_target - x1) * (y11 - y01) / (x1 - x0)
    
    # Interpolate in the z direction
    final_y = interp_x0 + (z_target - z0) * (interp_x1 - interp_x0) / (z1 - z0)
    
    return final_y

                
