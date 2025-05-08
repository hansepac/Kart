import pygame as pg

def draw_boost_bar(screen, current_value, max_value, boost_threshold, x = 20, y = 100):
    # Bar size
    bar_width = 30
    bar_height = 200

    # Clamp value between 0 and max_value
    current_value = max(0, min(current_value, max_value))

    # Calculate fill height
    fill_height = int((current_value / max_value) * bar_height)
    bar_color = (50, 150 + int((current_value-boost_threshold)/(max_value-boost_threshold)*75), 50) if current_value > boost_threshold else (100, 10, 10)
    bar_bg_color = (100, 50, 50)

    # Background (gray)
    pg.draw.rect(screen, bar_bg_color, (x, y, bar_width, bar_height), border_radius=5)
    # pg.draw.rect(screen, bar_color, (x, y, bar_width, bar_height), border_radius=5)

    # Fill (blue)
    pg.draw.rect(screen, bar_color, (x, y + bar_height - fill_height, bar_width, fill_height), border_radius=5)
