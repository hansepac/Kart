from __init__ import FRAME_RATE, clock, gameState, onlineState
import pygame as pg
import psutil
import os
import core
from input import game_end_check
from core.game import game_init

# GAME LOOP
game_running = True
dt = 1/FRAME_RATE

try:
    while game_running:
        # WAIT TILL FRAME RATE
        dt = 0.001 * clock.tick(FRAME_RATE)
        # Get all events
        events = pg.event.get()
        # Check if window "X" is pressed, or ESC
        game_running = game_end_check(events)
        # UPDATE ITEMS
        gameState = core.update(events, dt, gameState, onlineState)
        # DRAW SCREEN
        core.draw(gameState)
        # UPDATE DISPLAY
        pg.display.update()
finally:
    # Cleanup
    print("Terminating server process...")
    parent = psutil.Process(os.getpid())
    for child in parent.children(recursive=True):
        child.kill()
        print(f"Killed child process: {child.pid}")
    print("Server terminated")
    pg.quit()