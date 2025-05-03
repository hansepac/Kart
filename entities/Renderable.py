from abc import ABC, abstractmethod
from __init__ import pg
import numpy as np

class Renderable(ABC):
    def __init__(self):
        self.screen_depth = 0

    @abstractmethod
    def recalculate_screen_pos(self, camera):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

# used for drawing terrain triangles
class TerrainTriangle(Renderable):
    def __init__(self, homo_verts, camera, colour, skycolour):
        super().__init__()
        self.homo_verts = homo_verts
        self.colour = tuple([*colour])
        self.skycolour = skycolour

        # initially calculate screen_verts and depth
        self.screen_verts = camera.drawTriangle(self.homo_verts)
        if len(self.screen_verts) > 0:
            self.screen_depth = np.mean(self.screen_verts[:, 2])
        else:
            self.screen_depth = 0

    def recalculate_screen_pos(self, camera):
        # calculate screen_verts and depth
        self.screen_verts = camera.drawTriangle(self.homo_verts)
        # self.screen_verts = camera.getScreenCoords(self.homo_verts)
        if len(self.screen_verts) > 0:
            self.screen_depth = np.mean(self.screen_verts[:, 2])
        else:
            self.screen_depth = 0

    def draw(self, screen):
        # draw the object and calculate 
        # if np.linalg.norm(self.screen_verts[0]) > 1 and np.linalg.norm(self.screen_verts[1]) > 1 and np.linalg.norm(self.screen_verts[2]) > 1:
            # pg.draw.polygon(screen, self.colour, list(np.array(self.screen_verts)[:, 0:2]))
        #     pg.draw.lines(screen, (255, 255, 255), closed=True, points=list(self.screen_verts[:, 0:2]))

        # fade triangles as they are farther away
        render_color = smooth_color_transition(self.colour, self.skycolour, self.screen_depth, transition_point=0.9, steepness=20)

        if len(self.screen_verts) > 2:
            pg.draw.polygon(screen, render_color, list(np.array(self.screen_verts)[:, 0:2]))
            # pg.draw.lines(screen, (255, 255, 255), closed=True, points=list(np.array(self.screen_verts)[:, 0:2]))

# a renderable specific to drivers
class DriverSprite(Renderable):
    def __init__(self, driver_object, camera):
        super().__init__()
        self.homoloc = driver_object.get_homo_pos() 
        self.driver_object = driver_object

        # initially calculate screenloc and depth
        self.screenloc = camera.getScreenCoords([self.homoloc])[0]
        self.screen_depth = self.screenloc[2]


        shadow_loc = self.homoloc
        shadow_loc[1] = self.driver_object.terrainDynamic.get_ground_height(self.driver_object.pos)
        self.shadow_loc = camera.getScreenCoords([shadow_loc])[0]


        self.carImg = pg.image.load('assets/car1_basic.png')

    def recalculate_screen_pos(self, camera):
        self.screenloc = camera.getScreenCoords([self.homoloc])[0]
        shadow_loc = self.homoloc
        shadow_loc[1] = self.driver_object.terrainDynamic.get_ground_height(self.driver_object.pos)
        self.shadow_loc = camera.getScreenCoords([shadow_loc])[0]

    def draw(self, screen):
        if np.linalg.norm(self.screenloc) > 1:
            pg.draw.circle(screen, (50, 50, 50), (self.shadow_loc[0], self.shadow_loc[1]), 5)
            scaled_img = pg.transform.scale(self.carImg, (self.carImg.get_width() // 3, self.carImg.get_height() // 3))
            img_rect = scaled_img.get_rect(center=(self.screenloc[0], self.screenloc[1]))
            screen.blit(scaled_img, img_rect)

        

# basically the same as the dots we used earlier. 
class SimpleSprite(Renderable):
    def __init__(self, screen_depth, winx, winy):
        super().__init__()

        self.winx, self.winy = winx, winy
        self.color = (255, 255, 255)
        self.size = 5

    def draw(self, screen):
        pg.draw.circle(screen, self.color, (self.win_x, self.win_y), self.size)

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
