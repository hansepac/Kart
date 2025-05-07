from abc import ABC, abstractmethod
import numpy as np
import pygame as pg

class Renderable(ABC):
    def __init__(self):
        self.screen_depth = 0
        self.homo_coords = []
        self.screen_coords = []

    @abstractmethod
    def draw(self, screen):
        pass


def is_on_visible_side(renderable, plane_point, normal):
    vectors = np.array(renderable.homo_coords)[:, :3] - plane_point  # discard homogeneous coord
    dots = np.dot(vectors, normal)
    return np.any(dots > 0)


def calculateRenderableScreenCoords(camera, nontriangle_renderables, triangle_renderables):
    ''' This function will pass in all renderables to the camera as an array so that 
    the computation can be done in C rather than with a python for loop. '''

    # filter by if renderable is even in view
    '''It turned to to be faster to just render all of them rather than taking the time to 
    figure out if they should be rendered or not. '''
    

    homo_coords_list = []
    for renderable in nontriangle_renderables:
        homo_coords_list += renderable.homo_coords

    screen_coords = camera.getScreenCoords(homo_coords_list)

    # add buffer 
    buffer = 0
    mask = np.all(screen_coords == 0, axis=1)
    screen_coords[:, 0] = screen_coords[:, 0]*(camera.nx + 2*buffer)/camera.nx - buffer
    screen_coords[:, 1] = screen_coords[:, 1]*(camera.ny + 2*buffer)/camera.ny - buffer
    screen_coords[mask, :] = 0

    j = 0
    for i in range(len(nontriangle_renderables)):
        # after we calculate all the screen coords, pass them out again. 
        jn = len(nontriangle_renderables[i].homo_coords) + j
        nontriangle_renderables[i].screen_coords = screen_coords[j:jn]
        nontriangle_renderables[i].screen_depth = np.average(np.array(screen_coords[j:jn])[:, 2])
        
        j = jn

    # now do the trianles
    '''It ended up being faster to just do triangle rendering for every triangle,
    rather than taking the time to figure out if it actually need that or not. '''

    new_triangle_renderables = []
    for triangle_renderable in triangle_renderables:
        new_triangle_renderables.append(render_triangle(triangle_renderable, camera))
    

    return nontriangle_renderables + new_triangle_renderables


# this function is incase we want to do multi-processing on this
def render_triangle(triangle_renderable, camera):
    triangle_renderable.triangle_rendering = True
    triangle_renderable.screen_coords = camera.drawTriangle(triangle_renderable.homo_coords)
    if len(triangle_renderable.screen_coords) > 1:
        triangle_renderable.screen_depth = np.max(np.array(triangle_renderable.screen_coords)[:, 2])
    elif len(triangle_renderable.screen_coords) == 1:
        triangle_renderable.screen_depth = triangle_renderable.screen_coords[0][2]
    else:
        triangle_renderable.screen_depth = 0

    return triangle_renderable

# used for drawing terrain triangles
class TerrainTriangle(Renderable):
    def __init__(self, homo_coords, camera, colour, skycolour):
        super().__init__()
        self.homo_coords = homo_coords
        self.colour = tuple([*colour])
        self.skycolour = skycolour

        # placeholder
        self.screen_coords = None
        self.screen_depth = 0

        self.triangle_rendering = False


    def draw(self, screen):
        # draw the object and calculate 
        render_color = smooth_color_transition(self.colour, self.skycolour, self.screen_depth, transition_point=0.98, steepness=40)
        
        if self.triangle_rendering:
            if len(self.screen_coords) > 2:
                pg.draw.polygon(screen, render_color, list(np.array(self.screen_coords)[:, 0:2]))
        else:   
            if np.linalg.norm(self.screen_coords[0]) > 0 and np.linalg.norm(self.screen_coords[1]) > 0 and np.linalg.norm(self.screen_coords[2]) > 0 :
                pg.draw.polygon(screen, render_color, list(np.array(self.screen_coords)[:, 0:2]))
                # pg.draw.lines(screen, (255, 255, 255), closed=True, points=list(np.array(self.screen_verts)[:, 0:2]))

# a renderable specific to drivers
class DriverSprite(Renderable):
    def __init__(self, driver_object, camera):
        super().__init__()
        self.homo_coords = [driver_object.get_homo_pos()]
        self.driver_object = driver_object

        # initially calculate screenloc and depth
        self.screen_coords = None
        self.screen_depth = 0

        

        shadow_loc = self.homo_coords[0].copy()
        shadow_loc[1] = self.driver_object.terrainDynamic.get_ground_height(self.driver_object.pos)
        self.homo_coords.append(shadow_loc)

        # choose image
        driver_angle = np.atan2(driver_object.direction_unitvec[2], driver_object.direction_unitvec[0]) + np.pi/2
        relative_angle = (driver_angle - camera.phi) % (2*np.pi)
        division = round(relative_angle / (np.pi/4)) % 8

        # turn more if in first person 
        if driver_object.drift_direction > 0.5:
            division = (division + 1) % 8
        elif driver_object.drift_direction < -0.5:
                division = (division - 1) % 8

        self.carImg = pg.image.load(f'assets/car{driver_object.car_sprite}_{division}.png')
        self.map_icon = self.carImg

    def draw(self, screen):

        if np.linalg.norm(self.screen_coords[1]) > 0:
                scale_factor = 0.25*(1 - self.screen_coords[1][2])**(-1)
                shadow_rect = pg.Rect(0,0,80/scale_factor,40/scale_factor)
                shadow_rect.center = (self.screen_coords[1][0], self.screen_coords[1][1])
                pg.draw.ellipse(screen, (50, 50, 50), shadow_rect)

        if np.linalg.norm(self.screen_coords[0]) > 1:
            scale_factor = 0.7*(1 - self.screen_coords[0][2])**(-1)
            scaled_img = pg.transform.scale(self.carImg, (self.carImg.get_width() /scale_factor, self.carImg.get_height() /scale_factor))
            img_rect = scaled_img.get_rect(center=(self.screen_coords[0][0], self.screen_coords[0][1] - 0.1*scaled_img.get_height()))
            screen.blit(scaled_img, img_rect)

class FlagSprite(Renderable):
    def __init__(self, flag_pos, camera, isCurrent = False, isLast = False):
        super().__init__()
        self.homo_coords = [np.array([*flag_pos, 1])]
        
        # initially calculate screenloc and depth
        self.screen_coords = None
        self.screen_depth = 0

        self.flagImg = pg.image.load('assets/flag_green.png') if isCurrent else pg.image.load('assets/flag_red.png')
        if isLast:
            self.flagImg = pg.image.load('assets/sprite_finish.png')
        self.map_icon = self.flagImg

    def draw(self, screen):
        if np.linalg.norm(self.screen_coords[0]) > 1:
            scale_factor = 0.3*(1 - self.screen_depth)**(-1)
            scaled_img = pg.transform.scale(self.flagImg, (self.flagImg.get_width() / scale_factor, self.flagImg.get_height() / scale_factor))
            img_rect = scaled_img.get_rect(center=(self.screen_coords[0][0], self.screen_coords[0][1] - int(scaled_img.get_height()*0.6)))
            screen.blit(scaled_img, img_rect)

class TreeSprite(Renderable):
    def __init__(self, tree_homo_pos, biome_idx):
        super().__init__()
        self.homo_coords = [tree_homo_pos]

        self.screen_coords = None
        self.screen_depth = 0

        if biome_idx == 0:
            self.treeImg = pg.image.load('assets/rocks.png')
        elif biome_idx == 1:
            self.treeImg = pg.image.load('assets/Catus.png')
        elif biome_idx == 2:
            self.treeImg = pg.image.load('assets/pine-tree-isaiah658.png')
        else:
            self.treeImg = pg.image.load('assets/arvore.png')

        self.map_icon = self.treeImg

    def draw(self, screen):
        if np.linalg.norm(self.screen_coords[0]) > 1:
            scale_factor = 0.05*(1 - self.screen_depth)**(-1)
            scaled_img = pg.transform.scale(self.treeImg, (self.treeImg.get_width() / scale_factor, self.treeImg.get_height() / scale_factor))
            img_rect = scaled_img.get_rect(center=(self.screen_coords[0][0], self.screen_coords[0][1] - int(scaled_img.get_height()*0.5)))
            screen.blit(scaled_img, img_rect)



import math

def smooth_color_transition(color1, color2, t, transition_point=0.8, steepness=10.0):
    """
    Transitions from color1 to color2 using a sigmoid curve.
    
    Parameters:
        color1 (tuple): Starting color (R, G, B)
        color2 (tuple): Ending color (R, G, B)
        t (float): Unbounded transition parameter.
        transition_point (float): The point in [0, 1] where the second color takes over.
        steepness (float): Controls how sharply the transition occurs.
    
    Returns:
        tuple: Interpolated color.
    """
    # Clamp t and transition_point to [0, 1]
    t = max(0.0, min(1.0, t))
    transition_point = max(0.0, min(1.0, transition_point))

    if transition_point == 0:
        eased_t = 1.0
    elif transition_point == 1:
        eased_t = 0.0
    else:
        # Scale t to center the sigmoid at the transition point
        x = (t - transition_point) * steepness
        eased_t = 1 / (1 + math.exp(-x))  # sigmoid function

    return tuple(
        (1 - eased_t) * c1 + eased_t * c2 for c1, c2 in zip(color1, color2)
    )
