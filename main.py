from __init__ import FRAME_RATE
import pygame as pg
import core
from input import game_end_check
from core.game import game_init

# INITIALIZE FRAME RATE STUFF
delta_time = 0.0
clock = pg.time.Clock()

# GAME LOOP
game_init()
game_running = True

while game_running:
    # Check if window "X" is pressed, or ESC
    game_running = game_end_check()
    # UPDATE ITEMS
    core.update()
    # DRAW SCREEN
    core.draw()
    # UPDATE DISPLAY
    pg.display.update()
    # WAIT TILL FRAME RATE
    delta_time = 0.001 * clock.tick(FRAME_RATE)

# Cleanup and close
# client_socket.close()
pg.quit()