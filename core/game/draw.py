from __init__ import screen, camera, entities, keyboard
from pygame import gfxdraw as dr
import pygame as pg

font = pg.font.SysFont(None, 30)

def draw():
    # Clear Screen
    screen.fill((0,0,0))


    debug_text = [
        f"Camera Pos: {camera.x}, {camera.y}, {camera.z}",
        f"Camera Angle: {camera.phi}, {camera.theta}",
        f"FPS: {round(pg.time.Clock().get_fps())}",
        f"Entities: {len(entities)}",
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

    # Draw all entities
    for entity in entities:
        entity_pos = camera.getScreenCoords([entity.get_pos()])[0]
        # entity.size = entity_pos[2]
        if entity_pos[0] < camera.nx and entity_pos[0] > 0 and entity_pos[1] < camera.ny and entity_pos[1] > 0 and entity_pos[2] < 0:
            entity.draw(screen, round(entity_pos[0]), round(entity_pos[1]))
