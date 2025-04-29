import numpy as np
from noise import pnoise2

class TerrainGrid:
    def __init__(self, num_x, num_z, grid_spacing = 1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, nx = 100, nz = 100, center = np.array([0, 0, 0])):
        self.num_x = num_x
        self.num_z = num_z
        self.center = center 

        self.grid_spacing = grid_spacing
        self.nx = nx 
        self.nz = nz # per tile

        # generate seed here so it makes it continuous
        colour_base = np.random.randint(0, 1000)
        height_base_large = np.random.randint(0, 1000)
        detail_base = np.random.randint(0, 1000)


        self.grid = [] # we'll populate the second dimension later
        self.centers = np.zeros((num_z, num_x, 3))

        for j in range(num_z):
            row = []
            for i in range(num_x):
                tile_center = self.center + np.array([(1/2 + i - num_x/2)*grid_spacing*nx, 0, (1/2 + j - num_z/2)*grid_spacing*nz])
                row.append(Terrain(grid_spacing=grid_spacing, noise_density_large=noise_density_large, detail_density=detail_density,
                                   noise_height_large=noise_height_large, detail_height=detail_height, nx=nx, nz=nz, center=tile_center, 
                                   colour_base=colour_base, height_base_large=height_base_large, detail_base=detail_base))
                self.centers[j, i, :] = tile_center
            self.grid.append(row)

    def get_grid_tile(self, pos_3d):
        # get grid indices to determine tile of interest
        i = round((pos_3d[0] - self.center[0])/self.grid_spacing/self.nx - 1/2 + self.num_x/2)
        j = round((pos_3d[2] - self.center[2])/self.grid_spacing/self.nz - 1/2 + self.num_z/2)
        if i > -1 and j > -1 and i < self.num_x and j < self.num_z:
            return self.grid[j][i]
        else:
            return None

    def get_normal_vector(self, pos_3d):
        tile = self.get_grid_tile(pos_3d)
        if tile is not None:
            return tile.get_normal_vector(pos_3d)
        else:
            return np.array([0, 1, 0])

    def get_ground_height(self, pos_3d):
        tile = self.get_grid_tile(pos_3d)
        if tile is not None:
            return tile.get_ground_height(pos_3d)
        else:
            return 0


class Terrain:
    def __init__(self, grid_spacing = 1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, 
                 nx = 25, nz = 25, center = np.array([0, 0, 0]), 
                 colour_base = np.random.randint(0, 1000), height_base_large = np.random.randint(0, 1000), detail_base = np.random.randint(0, 1000)):

        self.points = np.zeros((nz, nx, 3))
        self.homo_points = np.zeros((nx, nz, 4))
        self.colours_grid = np.zeros((nz, nx, 3))
        self.grid_spacing = grid_spacing
        self.center = center
        self.nx, self.nz = nx, nz

        # generate perlin stuff
        for i in range(nx):
            for j in range(nz):
                self.points[j, i, 0] = (i - nx/2)*grid_spacing + center[0]
                self.points[j, i, 2] = (j - nz/2)*grid_spacing + center[2]
                self.points[j, i, 1] = noise_height_large* pnoise2(i * noise_density_large + center[0]/grid_spacing - nx/2, 
                                                                   j * noise_density_large + center[2]/grid_spacing - nz/2, 
                                        base=height_base_large) + detail_height* pnoise2(i * detail_density + center[0]/grid_spacing - nx/2, 
                                                                                         j * detail_density + center[2]/grid_spacing - nz/2, 
                                                                                         base=detail_base)

                self.homo_points[j, i, 0:3] = self.points[j, i, :]
                self.homo_points[j, i, 3] = 1

                self.colours_grid[j, i, :] = get_color_on_spectrum(pnoise2(i * noise_density_large + center[0]/grid_spacing - nx/2, 
                                                                           j * noise_density_large + center[2]/grid_spacing - nz/2, base=colour_base))
                
        # pack homogeneous triangles
        homo_triangles = []
        colours = []
        for i in range(self.nx - 1):
            for j in range(self.nz - 1):
                triangle = [self.homo_points[j, i, :], self.homo_points[j, i+1, :], self.homo_points[j+1, i, :]]
                homo_triangles.append(triangle)
                colours.append(self.colours_grid[j, i, :])
                triangle = [self.homo_points[j, i+1, :], self.homo_points[j+1, i, :], self.homo_points[j+1, i+1, :]]
                homo_triangles.append(triangle)
                colours.append(self.colours_grid[j+1, i+1, :])
        self.homo_triangles = homo_triangles
        self.colours_triangles = colours

    def get_normal_vector(self, pos_3d):
        if pos_3d[0] > self.points[0, 0, 0] and pos_3d[0] < self.points[0, -1, 0] and pos_3d[2] > self.points[0, 0, 2] and pos_3d[2] < self.points[-1, 0, 2]:
            # get grid indices to determine square of interest
            i = int((pos_3d[0] - self.center[0])/self.grid_spacing + self.nx/2)
            j = int((pos_3d[2] - self.center[2])/self.grid_spacing + self.nz/2)

            # determine distance to both triangle edges
            d1 = np.linalg.norm(pos_3d[[0, 2]] - self.points[j, i, :][[0, 2]])
            d2 = np.linalg.norm(pos_3d[[0, 2]] - self.points[j+1, i+1, :][[0, 2]])

            # select triangle and compute normal
            if d1 < d2:
                P1, P2, P3 = self.points[j, i, :], self.points[j, i+1, :], self.points[j+1, i, :]
            else:
                P1, P2, P3 = self.points[j+1, i+1, :], self.points[j, i+1, :], self.points[j+1, i, :]

            v1 = np.array(P2) - np.array(P1)
            v2 = np.array(P3) - np.array(P1)
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            if normal[1] < 0:
                # this might never run, i'm not sure
                normal *= -1
            return normal
        else:
            # we aren't on the grid
            return np.array([0, 1, 0])
        
    def get_ground_height(self, pos_3d):
        if pos_3d[0] > self.points[0, 0, 0] and pos_3d[0] < self.points[0, -1, 0] and pos_3d[2] > self.points[0, 0, 2] and pos_3d[2] < self.points[-1, 0, 2]:
            # get grid indices to determine square of interest
            i = int((pos_3d[0] - self.center[0])/self.grid_spacing + self.nx/2)
            j = int((pos_3d[2] - self.center[2])/self.grid_spacing + self.nz/2)

            # determine distance to both triangle edges
            d1 = np.linalg.norm(pos_3d[[0, 2]] - self.points[j, i, :][[0, 2]])
            d2 = np.linalg.norm(pos_3d[[0, 2]] - self.points[j+1, i+1, :][[0, 2]])

            # use distances to interpolate triangles. 
            if d1 < d2:
                return interpolate_y(pos_3d[0], pos_3d[2], self.points[j, i, :], self.points[j, i+1, :], self.points[j+1, i, :]) 
            else:
                return interpolate_y(pos_3d[0], pos_3d[2], self.points[j+1, i+1, :], self.points[j, i+1, :], self.points[j+1, i, :])
        else:
            # we aren't on the grid
            return 0

        
def interpolate_y(x, z, P1, P2, P3):
    # Convert points into numpy arrays for easier manipulation
    P1 = np.array(P1)
    P2 = np.array(P2)
    P3 = np.array(P3)

    # Calculate vectors
    v1 = P2 - P1
    v2 = P3 - P1

    # Calculate the normal vector to the plane (cross product of v1 and v2)
    normal = np.cross(v1, v2)

    # Plane equation coefficients A, B, C
    A, B, C = normal

    # Calculate D (from one of the points, say P1)
    D = -(A * P1[0] + B * P1[1] + C * P1[2])

    # Solve for y given x and z
    y = -(A * x + C * z + D) / B

    return y
    

import matplotlib.colors as mcolors

# Define the color spectrum using RGB values
greens = ["#006400", "#228B22", "#32CD32", "#7CFC00", "#98FB98"]  # Dark to light green
browns = ["#8B4513", "#A52A2A", "#D2691E", "#F4A460", "#DEB887"]   # Dark to light brown
tans = ["#D2B48C", "#F4A300", "#D19C53", "#C0C0C0", "#F5F5DC"]    # Tan and beige
greys = ["#2F4F4F", "#696969", "#A9A9A9", "#D3D3D3", "#DCDCDC"]   # Dark to light grey

# Combine all colors into one list
color_list = greens + browns + tans + greys

# Create an interpolation function for color mapping
def create_color_gradient(colors, num_colors=100):
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", colors, N=num_colors)
    return cmap(np.linspace(0, 1, num_colors))

# Function to get RGB values based on input number in the range -1 to 1
def get_color_on_spectrum(number, color_list=color_list):
    # Ensure the number is between -1 and 1
    if number < -1 or number > 1:
        raise ValueError("Input number must be between -1 and 1")
    
    # Map the number from [-1, 1] to [0, 1]
    scaled_number = (number + 1) / 2
    
    # Create the color gradient
    color_spectrum = create_color_gradient(color_list)
    
    # Map the scaled number to an index on the spectrum
    index = int(scaled_number * (len(color_spectrum) - 1))
    
    # Return the RGB value corresponding to the input number
    rgb = color_spectrum[index]
    
    # Convert to 0-255 range (matplotlib returns RGB as floats between 0 and 1)
    return np.array([int(c * 255) for c in rgb])[0:3]

