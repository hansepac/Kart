from abc import ABC, abstractmethod
from __init__ import pg
import numpy as np

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


def calculateRenderableScreenCoords(camera, renderables_list):
    ''' This function will pass in all renderables to the camera as an array so that 
    the computation can be done in C rather than with a python for loop. '''

    # filter by if renderable is even in view
    filtered_renderables = renderables_list # [r for r in renderables_list if is_on_visible_side(r, np.array([camera.x, camera.y, camera.z]), np.array([np.sin(camera.phi)*np.cos(camera.theta), np.sin(camera.theta), -np.cos(camera.theta)*np.cos(camera.phi)]))]


    homo_coords_list = []
    for renderable in filtered_renderables:
        homo_coords_list += renderable.homo_coords

    screen_coords = camera.getScreenCoords(homo_coords_list)

    # add buffer 
    buffer = 0
    mask = np.all(screen_coords == 0, axis=1)
    screen_coords[:, 0] = screen_coords[:, 0]*(camera.nx + 2*buffer)/camera.nx - buffer
    screen_coords[:, 1] = screen_coords[:, 1]*(camera.ny + 2*buffer)/camera.ny - buffer
    screen_coords[mask, :] = 0

    j = 0
    for i in range(len(filtered_renderables)):
        # after we calculate all the screen coords, pass them out again. 
        jn = len(filtered_renderables[i].homo_coords) + j
        filtered_renderables[i].screen_coords = screen_coords[j:jn]
        filtered_renderables[i].screen_depth = np.average(np.array(screen_coords[j:jn])[:, 2])

        # check to see if it needs triangle rendering
        # if isinstance(filtered_renderables[i], TerrainTriangle):
        #     row_norms = np.linalg.norm(screen_coords[j:jn], axis=1)
        #     if np.sum(row_norms > 0) < len(filtered_renderables[i].homo_coords):
                # do triangle rendering
        #        pass
                # filtered_renderables[i].triangle_rendering = True
                # filtered_renderables[i].screen_coords = camera.drawTriangle(filtered_renderables[i].homo_coords)
                # if len(filtered_renderables[i].screen_coords) > 1:
                #     filtered_renderables[i].screen_depth = np.average(np.array(filtered_renderables[i].screen_coords)[:, 2])
                # elif len(filtered_renderables[i].screen_coords) == 1:
                #     filtered_renderables[i].screen_depth = filtered_renderables[i].screen_coords[0][2]
                # else:
                #     filtered_renderables[i].screen_depth = 0
        j = jn


    return filtered_renderables



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
        render_color = smooth_color_transition(self.colour, self.skycolour, self.screen_depth, transition_point=0.9, steepness=20)
        
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

        self.carImg = pg.image.load('assets/car1_basic.png')

    def draw(self, screen):
        if np.linalg.norm(self.screen_coords[0]) > 1:
            shadow_rect = pg.Rect(0,0,80,40)
            shadow_rect.center = (self.screen_coords[1][0], self.screen_coords[1][1])
            pg.draw.ellipse(screen, (50, 50, 50), shadow_rect)
            
            scaled_img = pg.transform.scale(self.carImg, (self.carImg.get_width() // 3, self.carImg.get_height() // 3))
            img_rect = scaled_img.get_rect(center=(self.screen_coords[0][0], self.screen_coords[0][1]))
            screen.blit(scaled_img, img_rect)

class FlagSprite(Renderable):
    def __init__(self, flag_pos, camera, isCurrent = False):
        super().__init__()
        self.homo_coords = [np.array([*flag_pos, 1])]
        
        # initially calculate screenloc and depth
        self.screen_coords = None
        self.screen_depth = 0

        self.flagImg = pg.image.load('assets/flag_green.png') if isCurrent else pg.image.load('assets/flag_red.png')

    def draw(self, screen):
        if np.linalg.norm(self.screen_coords[0]) > 1:
            scale_factor = 0.3*(1 - self.screen_depth)**(-1)
            scaled_img = pg.transform.scale(self.flagImg, (self.flagImg.get_width() / scale_factor, self.flagImg.get_height() / scale_factor))
            img_rect = scaled_img.get_rect(center=(self.screen_coords[0][0], self.screen_coords[0][1] - int(scaled_img.get_height()*0.6)))
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
