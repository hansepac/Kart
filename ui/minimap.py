import pygame as pg
from math import cos, sin

font = pg.font.SysFont(None, 20)

def draw_minimap(screen, angle_from_vertical, center:tuple, radius = 100):
    
    # Draw needle
    x = center[0] + sin(angle_from_vertical) * radius
    y = center[1] - cos(angle_from_vertical) * radius
    pg.draw.line(screen, (255, 0, 0), center, (x, y), 4)

    # Draw center
    pg.draw.circle(screen, (255, 255, 255), center, 5)
