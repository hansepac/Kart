import pygame as pg
from math import radians, cos, sin

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




# --- Helper Functions ---
def angle_for_value(value, min_val, max_val):
    """Map value to angle between 135° and 45° (in radians)."""
    value = max(min(value, max_val), min_val)
    ratio = (value - min_val) / (max_val - min_val)
    return radians(135 - 270 * ratio)

def draw_speedometer(screen, value, center:tuple, radius = 150, min_val = 0, max_val = 800, tick_step = 20):
    # Draw outer circle
    pg.draw.arc(screen, (200, 200, 200), 
                    (center[0] - radius, center[1] - radius, radius*2, radius*2), 
                    radians(135), radians(45), 5)

    # Draw ticks
    for val in range(min_val, max_val + 1, tick_step):
        ang = angle_for_value(val, min_val, max_val)
        x1 = center[0] + cos(ang) * (radius - 10)
        y1 = center[1] - sin(ang) * (radius - 10)
        x2 = center[0] + cos(ang) * (radius)
        y2 = center[1] - sin(ang) * (radius)
        pg.draw.line(screen, (255, 255, 255), (x1, y1), (x2, y2), 2)

        # Label
        label = font.render(str(val), True, (255, 255, 255))
        lx = center[0] + cos(ang) * (radius - 25) - label.get_width() / 2
        ly = center[1] - sin(ang) * (radius - 25) - label.get_height() / 2
        screen.blit(label, (lx, ly))

    # Draw needle
    ang = angle_for_value(value, min_val, max_val)
    x = center[0] + cos(ang) * (radius - 30)
    y = center[1] - sin(ang) * (radius - 30)
    pg.draw.line(screen, (255, 0, 0), center, (x, y), 4)

    # Draw center
    pg.draw.circle(screen, (255, 255, 255), center, 5)

    # Value text
    val_text = font.render(f"Speed: {round(value, -1)}", True, (255, 255, 255))
    screen.blit(val_text, (center[0] - val_text.get_width()//2, center[1] - 50))
