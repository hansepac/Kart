from __init__ import FRAME_RATE, clock, gameState
import pygame as pg
import core
from input import game_end_check
from core.game import game_init

# GAME LOOP
game_init()
game_running = True
dt = 1/FRAME_RATE

while game_running:
    # WAIT TILL FRAME RATE
    dt = 0.001 * clock.tick(FRAME_RATE)
    # Get all events
    events = pg.event.get()
    # Check if window "X" is pressed, or ESC
    game_running = game_end_check(events)
    # UPDATE ITEMS
    gameState = core.update(events, dt, gameState)
    # DRAW SCREEN
    core.draw(gameState)
    # UPDATE DISPLAY
    pg.display.update()

# Cleanup and close
# client_socket.close()
pg.quit()