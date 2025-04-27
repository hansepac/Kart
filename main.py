from __init__ import FRAME_RATE, clock
import pygame as pg
import core
from input import game_end_check
from core.game import game_init

# GAME LOOP
game_init()
game_running = True

while game_running:
    # Get all events
    events = pg.event.get()
    # Check if window "X" is pressed, or ESC
    game_running = game_end_check(events)
    # UPDATE ITEMS
    core.update(events)
    # DRAW SCREEN
    core.draw()
    # UPDATE DISPLAY
    pg.display.update()
    # WAIT TILL FRAME RATE
    delta_time = 0.001 * clock.tick(FRAME_RATE)

# Cleanup and close
# client_socket.close()
pg.quit()