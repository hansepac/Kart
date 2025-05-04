# General Imports
import pygame as pg
import psutil
import os

# Setup pygame
pg.display.set_caption('Kart')
pg.display.init()
pg.init()


# Game Imports
import core
from input import game_end_check
from utils.states import GameState, OnlineState
from utils.cores import Core

c = Core()

# WINDOW SETUP
c.screen = pg.display.set_mode((1920,1080), pg.RESIZABLE, vsync=1)

# GAME SETUP
FRAME_RATE = 120
c.DEV_MODE = True

# Init game clock
c.clock = pg.time.Clock()

# Game States
c.gameState = GameState(0) # {0: TITLE, 1: CHAR_SELEC, 2: IN_GAME, 3: SETTINGS}
c.onlineState = OnlineState(0) # {0: LOCAL, 1: CLIENT, 2: HOST}

# Menu Screens
from ui import MenuCore
win_x, win_y = c.screen.get_size()
mc = MenuCore(c.screen, c.gameState, c.onlineState, win_x, win_y)

# GAME LOOP
c.game_running = True

try:
    while c.game_running:
        # Get window size
        c.win_x, c.win_y = c.screen.get_size()
        # WAIT TILL FRAME RATE
        c.dt = 0.001 * c.clock.tick(FRAME_RATE)
        # Get all events
        c.events = pg.event.get()
        # Check if window "X" is pressed, or ESC
        c.game_running = game_end_check(c.events)
        # UPDATE ITEMS
        c = core.update(c, mc)
        # DRAW SCREEN
        core.draw(c, mc)
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