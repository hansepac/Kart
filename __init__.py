import os

# WINDOW SETUP
import pygame as pg
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
screen = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT), pg.RESIZABLE, vsync=1)
pg.display.set_caption('Kart')
pg.display.init()
pg.init()

# GAME SETUP
FRAME_RATE = 60
CAMERA_SCALE = 60

# Game States
from utils.states import GameState, OnlineState
gameState = GameState(1) # {0: TITLE, 1: IN_GAME}
onlineState = OnlineState(1) # {0: LOCAL, 1: ONLINE}

# Keyboard
from input.Controller import Keyboard
keyboard = Keyboard()

# Example
from entities.Player import Player
window_x, window_y = screen.get_size()
player = Player(pg.Vector2(window_x/2, window_y/2))







# Don't mind this stuff for now

# DEV = True

# # SERVER SETUP
# from dotenv import load_dotenv
# if DEV:
#     load_dotenv(".env.dev")
# else:
#     load_dotenv(".env.prod")

# HOST = os.getenv("HOST")
# PORT = int(os.getenv("PORT"))

# # CONNECTING TO SERVER
# import socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((HOST, PORT))
# local_address = client_socket.getsockname()

