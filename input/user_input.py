import pygame as pg

def game_end_check(events):
    """Ends game if escape is pressed or if the window is closed"""
    for event in events:
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return False
    return True