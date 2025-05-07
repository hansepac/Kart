import pygame as pg
import numpy as np
from entities.Renderable import TreeSprite

font = pg.font.SysFont(None, 20)

def draw_minimap(screen, map_pos, map_direction_unitvec, non_triangle_renderables, origin:tuple, radius = 100, buffer=20):
    
    map_scale_factor = 50

    mm_screen = pg.Surface((2*radius + 2*buffer, 2*radius + 2*buffer), pg.SRCALPHA)
    # # Draw needle
    # x = center[0] + sin(angle_from_vertical) * radius
    # y = center[1] - cos(angle_from_vertical) * radius
    # pg.draw.line(screen, (255, 0, 0), center, (x, y), 4)

    
    pg.draw.circle(mm_screen, (100, 100, 100, 128), (radius + buffer, radius + buffer), radius)
    pg.draw.circle(mm_screen, (100, 100, 100, 255), (radius + buffer, radius + buffer), radius, width=4)

    # draw drivers
    for renderable in non_triangle_renderables:
        displacement = np.array([renderable.homo_coords[0][0], renderable.homo_coords[0][2]]) - np.array([map_pos[0], map_pos[2]])
        dist = np.linalg.norm(displacement)*map_scale_factor
        
        phi1 = np.atan2(map_direction_unitvec[2], map_direction_unitvec[0])
        phi2 = np.atan2(displacement[1], displacement[0])
        angle_between = (phi2 - phi1 ) % (2*np.pi)

        if dist > radius:
            dist = radius
        
        draw_pos = (dist*np.sin(angle_between) + radius + buffer, -dist*np.cos(angle_between) + radius + buffer)
        if isinstance(renderable, TreeSprite):
            pg.draw.circle(mm_screen, (150, 150, 150), draw_pos, 3)
        else:
            scaled_img = pg.transform.scale(renderable.map_icon, (20, 20))
            img_rect = scaled_img.get_rect(center=draw_pos)
            mm_screen.blit(scaled_img, img_rect)


    # blit the minimap to the screen
    screen.blit(mm_screen, origin)
