import pygame as pg

def game_end_check():
    """Ends game if escape is pressed or if the window is closed"""
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            return False
    return True