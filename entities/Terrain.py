import numpy as np
from noise import pnoise2
import random

class TerrainDynamicCoordinator:
    def __init__(self, grid_spacing = 0.1, noise_density_large = 0.01, detail_density = 0.12, noise_height_large = 3, detail_height = 0.3, color_density = 0.01, radius=20):
        self.grid_spacing = grid_spacing
        self.noise_density_large = noise_density_large
        self.detail_density = detail_density
        self.noise_height_large = noise_height_large
        self.detail_height = detail_height
        self.color_density = color_density
        self.radius = radius

        # generate seed here so it makes it continuous
        self.height_base_large = np.random.randint(0, 1000)
        self.detail_base = np.random.randint(0, 1000)
        self.colour_base = np.random.randint(0, 1000, 4) # dimension determines number of biomes

        self.tree_seed = np.random.randint(0, 1000)

    def get_seed_json(self):
        return {
            "colour_base": self.colour_base.tolist(),
            "height_base_large": self.height_base_large,
            "detail_base": self.detail_base,
            "noise_density_large": self.noise_density_large,
            "detail_density": self.detail_density,
            "noise_height_large": self.noise_height_large,
            "detail_height": self.detail_height,
            "grid_spacing": self.grid_spacing
        }
    
    def overwrite_seed(self, seed_json):
        self.colour_base = np.array(seed_json["colour_base"])
        self.height_base_large = seed_json["height_base_large"]
        self.detail_base = seed_json["detail_base"]
        self.noise_density_large = seed_json["noise_density_large"]
        self.detail_density = seed_json["detail_density"]
        self.noise_height_large = seed_json["noise_height_large"]
        self.detail_height = seed_json["detail_height"]
        self.grid_spacing = seed_json["grid_spacing"]

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
        self.trees = np.zeros((self.coordinator.radius*2, self.coordinator.radius*2), dtype=int) # 1 if tree and 0 if not
        self.biomes = np.zeros((self.coordinator.radius*2, self.coordinator.radius*2), dtype=int) # index of biome color

        self.center = center

        # hard coded colors
        self.colors = [np.array([145, 145, 145]), np.array([204, 102, 0]), np.array([102, 102, 51]), np.array([51, 153, 51])]

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
        
        self.trees[j, i] = self.has_tree(self.points[j, i, 0], self.points[j, i, 2])    

        self.homo_points[j, i, 0:3] = self.points[j, i, :]
        self.homo_points[j, i, 3] = 1

        self.colours_grid[j, i, :], self.biomes[j, i] = self.calculate_perlin_color(i, j) 

        

    def has_tree(self, x, z):
        combined_seed = hash((x, z, self.coordinator.tree_seed))
        rng = random.Random(combined_seed)
        return int(rng.random() <  0.01)

    def calculate_perlin_color(self, i, j):
        # first get random unit vector 
        unit_vec = np.zeros_like(self.coordinator.colour_base, dtype=float)
        for k in range(unit_vec.shape[0]):
            unit_vec[k] = pnoise2((i - self.coordinator.radius + self.center[0]/self.coordinator.grid_spacing)* self.coordinator.color_density, 
                                  (j - self.coordinator.radius + self.center[2]/self.coordinator.grid_spacing) * self.coordinator.color_density, base=self.coordinator.colour_base[k])
            unit_vec[k] += 0.5*pnoise2((i - self.coordinator.radius + self.center[0]/self.coordinator.grid_spacing)* self.coordinator.color_density*2, 
                                  (j - self.coordinator.radius + self.center[2]/self.coordinator.grid_spacing) * self.coordinator.color_density*2, base=self.coordinator.colour_base[k] + 10)
    
        if np.linalg.norm(unit_vec) == 0:
            unit_vec += np.ones_like(unit_vec)

        # now do the quantum square and normalize to get a probability vector
        p_vec = unit_vec**2 / np.linalg.norm(unit_vec)**2

        final_color = np.zeros(3)
        for i in range(len(p_vec)):
            final_color += p_vec[i]*self.colors[i]

        return final_color.astype(int), get_index_of_largest_element(p_vec)

    def get_trees(self):
        homo_trees = []
        biomes = []
        for i in range(self.trees.shape[1]):
            for j in range(self.trees.shape[0]):
                if self.trees[j, i] == 1:
                    homo_trees.append(self.homo_points[j, i, :])
                    biomes.append(self.biomes[j, i])
        return homo_trees, biomes

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
                self.trees[:, :-1] = self.trees[:, 1:]
                self.biomes[:, :-1] = self.biomes[:, 1:]

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
                self.trees[:, 1:] = self.trees[:, :-1]
                self.biomes[:, 1:] = self.biomes[:, :-1]

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
                self.trees[:-1, :] = self.trees[1:, :]
                self.biomes[:-1, :] = self.biomes[1:, :]

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
                self.trees[1:, :] = self.trees[:-1, :]
                self.biomes[1:, :] = self.biomes[:-1, :]

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
    


def get_index_of_largest_element(arr):
    """
    Returns the index of the largest element in the array.

    Args:
        arr: A list of numbers.

    Returns:
        The index of the largest element in the array.
    """
    if not list(arr):
        return -1  # Return -1 for an empty array
    max_index = 0
    for i in range(1, len(list(arr))):
        if list(arr)[i] > list(arr)[max_index]:
            max_index = i
    return max_index
