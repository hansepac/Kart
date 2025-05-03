import numpy as np
from noise import pnoise2

class TerrainDynamicCoordinator:
    def __init__(self, grid_spacing = 1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, radius=20, center = np.array([0, 0, 0])):
        self.grid_spacing = grid_spacing
        self.noise_density_large = noise_density_large
        self.detail_density = detail_density
        self.noise_height_large = noise_height_large
        self.detail_height = detail_height
        self.radius = radius

        # generate seed here so it makes it continuous
        self.colour_base = np.random.randint(0, 1000)
        self.height_base_large = np.random.randint(0, 1000)
        self.detail_base = np.random.randint(0, 1000)

    def get_rough_height(self, pos_3d):
        '''Returns the height of the perlin function. It might not line up exactly with the ground because the 
        ground is quantized to a grid, and has linear interpolation, while this doesn't take into account the grid.'''

        return self.noise_height_large* pnoise2((pos_3d[0]/self.grid_spacing) * self.noise_density_large, 
                                                            (pos_3d[2]/self.grid_spacing) * self.noise_density_large, 
                                base=self.height_base_large) + self.detail_height* pnoise2((pos_3d[0]/self.grid_spacing) * self.detail_density, 
                                                                                    (pos_3d[2]/self.grid_spacing) * self.detail_density, 
                                                                                    base=self.detail_base)




class TerrainDynamic:
    def __init__(self, coordinator, center = np.array([0, 0, 0])):
        self.coordinator = coordinator


        self.points = np.zeros((self.coordinator.radius*2, self.coordinator.radius*2, 3))
        self.homo_points = np.zeros((self.coordinator.radius*2, self.coordinator.radius*2, 4))
        self.colours_grid = np.zeros((self.coordinator.radius*2, self.coordinator.radius*2, 3))

        self.center = center

        # generate initial area
        for i in range(self.coordinator.radius*2):
            for j in range(self.coordinator.radius*2):
                self.calculate_perlin_point(i, j)

        # pack homogeneous triangles
        self.pack_triangles()

    def calculate_perlin_point(self, i, j):
        self.points[j, i, 0] = (i - self.coordinator.radius)*self.coordinator.grid_spacing + self.center[0]
        self.points[j, i, 2] = (j - self.coordinator.radius)*self.coordinator.grid_spacing + self.center[2]
        self.points[j, i, 1] = self.coordinator.noise_height_large* pnoise2((i - self.coordinator.radius + self.center[0]/self.coordinator.grid_spacing) * self.coordinator.noise_density_large, 
                                                            (j - self.coordinator.radius + self.center[2]/self.coordinator.grid_spacing) * self.coordinator.noise_density_large, 
                                base=self.coordinator.height_base_large) + self.coordinator.detail_height* pnoise2((i - self.coordinator.radius + self.center[0]/self.coordinator.grid_spacing) * self.coordinator.detail_density, 
                                                                                    (j - self.coordinator.radius + self.center[2]/self.coordinator.grid_spacing) * self.coordinator.detail_density, 
                                                                                    base=self.coordinator.detail_base)

        self.homo_points[j, i, 0:3] = self.points[j, i, :]
        self.homo_points[j, i, 3] = 1

        self.colours_grid[j, i, :] = get_color_on_spectrum(pnoise2((i - self.coordinator.radius + self.center[0]/self.coordinator.grid_spacing)* self.coordinator.noise_density_large, 
                                                                    (j - self.coordinator.radius + self.center[2]/self.coordinator.grid_spacing) * self.coordinator.noise_density_large, base=self.coordinator.colour_base))    

    def pack_triangles(self):
        homo_triangles = []
        colours = []
        for i in range(2*self.coordinator.radius - 1):
            for j in range(2*self.coordinator.radius - 1):
                triangle = [self.homo_points[j, i, :], self.homo_points[j, i+1, :], self.homo_points[j+1, i, :]]
                homo_triangles.append(triangle)
                colours.append(self.colours_grid[j, i, :])
                triangle = [self.homo_points[j, i+1, :], self.homo_points[j+1, i, :], self.homo_points[j+1, i+1, :]]
                homo_triangles.append(triangle)
                colours.append(self.colours_grid[j+1, i+1, :])
        self.homo_triangles = homo_triangles
        self.colours_triangles = colours

    def update_grid(self, pos_3d):
        while abs(pos_3d[0] - self.center[0]) > self.coordinator.grid_spacing:
            if pos_3d[0] - self.center[0] > 0:
                # move the center
                self.center += np.array([self.coordinator.grid_spacing, 0, 0])

                # shift existing points
                self.points[:, :-1, :] = self.points[:, 1:, :]
                self.homo_points[:, :-1, :] = self.homo_points[:, 1:, :]
                self.colours_grid[:, :-1, :] = self.colours_grid[:, 1:, :]

                # calculate new points
                for j in range(2*self.coordinator.radius):
                    self.calculate_perlin_point(2*self.coordinator.radius - 1, j)
            else:
                # move the center
                self.center -= np.array([self.coordinator.grid_spacing, 0, 0])

                # shift existing points
                self.points[:, 1:, :] = self.points[:, :-1, :]
                self.homo_points[:, 1:, :] = self.homo_points[:, :-1, :]
                self.colours_grid[:, 1:, :] = self.colours_grid[:, :-1, :]

                # calculate new points
                for j in range(2*self.coordinator.radius):
                    self.calculate_perlin_point(0, j)

        while abs(pos_3d[2] - self.center[2]) > self.coordinator.grid_spacing:
            if pos_3d[2] - self.center[2] > 0:
                # move the center
                self.center += np.array([0, 0, self.coordinator.grid_spacing])

                # shift existing points
                self.points[:-1, :, :] = self.points[1:, :, :]
                self.homo_points[:-1, :, :] = self.homo_points[1:, :, :]
                self.colours_grid[:-1, :, :] = self.colours_grid[1:, :, :]

                # calculate new points
                for i in range(2*self.coordinator.radius):
                    self.calculate_perlin_point(i, 2*self.coordinator.radius - 1)
            else:
                # move the center
                self.center -= np.array([0, 0, self.coordinator.grid_spacing])

                # shift existing points
                self.points[1:, :, :] = self.points[:-1, :, :]
                self.homo_points[1:, :, :] = self.homo_points[:-1, :, :]
                self.colours_grid[1:, :, :] = self.colours_grid[:-1, :, :]

                # calculate new points
                for i in range(2*self.coordinator.radius):
                    self.calculate_perlin_point(i, 0)

        # pack triangles again
        self.pack_triangles()


    def get_normal_vector(self, pos_3d):
        if pos_3d[0] > self.points[0, 0, 0] and pos_3d[0] < self.points[0, -1, 0] and pos_3d[2] > self.points[0, 0, 2] and pos_3d[2] < self.points[-1, 0, 2]:
            # get grid indices to determine square of interest
            i = int((pos_3d[0] - self.center[0])/self.coordinator.grid_spacing + self.coordinator.radius)
            j = int((pos_3d[2] - self.center[2])/self.coordinator.grid_spacing + self.coordinator.radius)

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
            i = int((pos_3d[0] - self.center[0])/self.coordinator.grid_spacing + self.coordinator.radius)
            j = int((pos_3d[2] - self.center[2])/self.coordinator.grid_spacing + self.coordinator.radius)

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


class TerrainGrid:
    def __init__(self, num_x, num_z, grid_spacing = 1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, nx = 100, nz = 100, origin = np.array([0, 0, 0])):
        self.num_x = num_x
        self.num_z = num_z
        self.origin = origin 

        self.grid_spacing = grid_spacing
        self.nx = nx 
        self.nz = nz # per tile

        # generate seed here so it makes it continuous
        colour_base = np.random.randint(0, 1000)
        height_base_large = np.random.randint(0, 1000)
        detail_base = np.random.randint(0, 1000)


        self.grid = [] # we'll populate the second dimension later
        self.origins = np.zeros((num_z, num_x, 3))

        for j in range(num_z):
            row = []
            for i in range(num_x):
                tile_center = self.origin + np.array([i*grid_spacing*nx, 0, j*grid_spacing*nz])
                row.append(Terrain(grid_spacing=grid_spacing, noise_density_large=noise_density_large, detail_density=detail_density,
                                   noise_height_large=noise_height_large, detail_height=detail_height, nx=nx+1, nz=nz+1, origin=tile_center, 
                                   colour_base=colour_base, height_base_large=height_base_large, detail_base=detail_base))
                self.origins[j, i, :] = tile_center
            self.grid.append(row)

    def get_grid_tile(self, pos_3d):
        # get grid indices to determine tile of interest
        i = int((pos_3d[0] - self.origin[0])/self.grid_spacing/self.nx)
        j = int((pos_3d[2] - self.origin[2])/self.grid_spacing/self.nz)
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
        
    def get_adjacent_tiles(self, pos_3d, direction_vec):
        # get grid indices to determine tile of interest
        i = int((pos_3d[0] - self.origin[0])/self.grid_spacing/self.nx)
        j = int((pos_3d[2] - self.origin[2])/self.grid_spacing/self.nz)
        if i > -1 and j > -1 and i < self.num_x and j < self.num_z:
            jm = (j + 1) % self.num_z
            im = (i + 1) % self.num_x
            jm2 = (j + 2) % self.num_z 
            im2 = (i + 2) % self.num_x

            returnlist = [self.grid[j][i]]
        
            phi = np.atan2(direction_vec[2], direction_vec[0])
            if phi < np.pi/4 and phi > -np.pi/4:
                returnlist += [self.grid[j][im], self.grid[j-1][im], self.grid[jm][im], 
                               self.grid[j-1][i], self.grid[jm][i], self.grid[j][i-1], 
                               self.grid[j][im2], self.grid[j-1][im2], self.grid[jm][im2]] 
            elif phi > np.pi/4 and phi < 3*np.pi/4:
                returnlist += [self.grid[jm][i], self.grid[jm][i-1], self.grid[jm][im], 
                               self.grid[j][i-1], self.grid[j][im], self.grid[j-1][i], 
                               self.grid[jm2][i], self.grid[jm2][i-1], self.grid[jm2][im]]  
            elif (phi > 3*np.pi/4 and phi < np.pi) or (phi > -np.pi and phi < -3*np.pi/4):
                returnlist += [self.grid[j][i-1], self.grid[j-1][i-1], self.grid[jm][i-1], 
                               self.grid[j-1][i], self.grid[jm][i], self.grid[j][im], 
                               self.grid[j][i-2], self.grid[j-1][i-2], self.grid[jm][i-2]] 
            else:
                returnlist += [self.grid[j-1][i], self.grid[j-1][i-1], self.grid[j-1][im], 
                               self.grid[j][i-1], self.grid[j][im], self.grid[jm][i], 
                               self.grid[j-2][i], self.grid[j-2][i-1], self.grid[j-2][im]]  

            return returnlist
        else:
            return []


class Terrain:
    def __init__(self, grid_spacing = 1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, 
                 nx = 25, nz = 25, origin = np.array([0, 0, 0]), 
                 colour_base = np.random.randint(0, 1000), height_base_large = np.random.randint(0, 1000), detail_base = np.random.randint(0, 1000)):

        self.points = np.zeros((nz, nx, 3))
        self.homo_points = np.zeros((nx, nz, 4))
        self.colours_grid = np.zeros((nz, nx, 3))
        self.grid_spacing = grid_spacing
        self.origin = origin
        self.nx, self.nz = nx, nz

        # generate perlin stuff
        for i in range(nx):
            for j in range(nz):
                self.points[j, i, 0] = i*grid_spacing + origin[0]
                self.points[j, i, 2] = j*grid_spacing + origin[2]
                self.points[j, i, 1] = noise_height_large* pnoise2((i + origin[0]/grid_spacing) * noise_density_large, 
                                                                   (j + origin[2]/grid_spacing) * noise_density_large, 
                                        base=height_base_large) + detail_height* pnoise2((i + origin[0]/grid_spacing) * detail_density, 
                                                                                         (j + origin[2]/grid_spacing) * detail_density, 
                                                                                         base=detail_base)

                self.homo_points[j, i, 0:3] = self.points[j, i, :]
                self.homo_points[j, i, 3] = 1

                self.colours_grid[j, i, :] = get_color_on_spectrum(pnoise2((i  + origin[0]/grid_spacing)* noise_density_large, 
                                                                           (j + origin[2]/grid_spacing) * noise_density_large, base=colour_base))
                
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
            i = int((pos_3d[0] - self.origin[0])/self.grid_spacing)
            j = int((pos_3d[2] - self.origin[2])/self.grid_spacing)

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
            i = int((pos_3d[0] - self.origin[0])/self.grid_spacing)
            j = int((pos_3d[2] - self.origin[2])/self.grid_spacing)

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

