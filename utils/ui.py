import pygame as pg

font = pg.font.SysFont(None, 30)

def draw_debug_text(surface, lines, color, padding=10):
    """Draw list of text lines to bottom-left of the screen."""
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    x = padding
    y = surface.get_height() - total_height - padding

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * line_height))