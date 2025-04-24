from __init__ import screen, camera, entities, keyboard
from pygame import gfxdraw as dr
import pygame as pg

font = pg.font.SysFont(None, 30)

def draw():
    # Clear Screen
    screen.fill((0,0,0))

    rendered_entities = 0

    # Draw all entities
    for entity in entities:
        entity_pos = camera.getScreenCoords([entity.get_pos()])[0]
        if entity_pos is not None:
            rendered_entities += 1
            # entity.size = entity_pos[2]
            entity.draw(screen, round(entity_pos[0]), round(entity_pos[1]))


    debug_text = [
        f"Camera Pos: {round(camera.x, 2)}, {round(camera.y, )}, {round(camera.z, 2)}",
        f"Camera Angle: {camera.phi}, {camera.theta}",
        f"FPS: {round(pg.time.Clock().get_fps())}",
        f"Entities Seen: {rendered_entities}"
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