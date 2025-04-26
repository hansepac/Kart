from __init__ import screen, camera, entities, mapMaster, firsttrack
from pygame import gfxdraw as dr
import numpy as np
import pygame as pg

font = pg.font.SysFont(None, 30)

def draw():
    # Clear Screen
    screen.fill((0,0,0))

    rendered_entities = 0

    mapMaster.draw(screen)

    # draw track
    # screenedgecoordsmat = camera.prepDrawEdges(firsttrack.track_edge_homocoords)
    for edge in firsttrack.track_edge_homocoords:
        screenedgecoords = camera.getScreenCoords(edge)
        if np.linalg.norm(screenedgecoords[0]) > 1 and np.linalg.norm(screenedgecoords[1]) > 1:
            pg.draw.line(screen, (255,255,255), list(screenedgecoords[0][0:2]), list(screenedgecoords[1][0:2]), 1)

    for rect in firsttrack.track_rect_homocoords:
        src = camera.getScreenCoords(rect)
        if np.linalg.norm(src[0]) > 1 and np.linalg.norm(src[1]) > 1 and np.linalg.norm(src[2]) > 1 and np.linalg.norm(src[3]) > 1:
            pg.draw.polygon(screen, (255, 228, 168), [src[0][0:2], src[1][0:2], src[2][0:2], src[3][0:2]])


    


    debug_text = [
        f"Camera Pos: {round(camera.x, 2)}, {round(camera.y, )}, {round(camera.z, 2)}",
        f"Camera Angle: {camera.phi}, {camera.theta}",
        f"FPS: {round(pg.time.Clock().get_fps())}",
        f"Entities Seen: {rendered_entities}",
        f"Number of edges in track: {len(firsttrack.edge_homocoords)}"
    ]

    def draw_lines_bottom_left(surface, lines, font, color, padding=10):
        """Draw list of text lines to bottom-left of the screen."""
        line_height = font.get_linesize()
        total_height = line_height * len(lines)
        x = padding
        y = surface.get_height() - total_height - padding

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y + i * line_height))





    draw_lines_bottom_left(screen, debug_text, font, (255, 255, 255))