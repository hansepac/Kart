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

DEBUG = True

# Game States
from utils.states import GameState, OnlineState
gameState = GameState(1) # {0: TITLE, 1: IN_GAME}
onlineState = OnlineState(1) # {0: LOCAL, 1: ONLINE}

# Keyboard
from input.Controller import Keyboard
pg.mouse.set_visible(False)
pg.event.set_grab(True) 
keyboard = Keyboard()

# Example
window_x, window_y = screen.get_size()

# Camera
from entities import Camera
from numpy import pi
camera = Camera(z = -10, theta = 0, phi = pi/2, nx = window_x, ny = window_y)

# Create Dots
from entities import Dots
entities = []
coords = [
    [0, 0, -2],
    [2.2, 0 , 0],
    [0, 0, 2],
    [1.1, 0, 1.1]
]

from random import randint
for i in range(1000):
    coords.append([randint(-10, 10), randint(-10, 10), randint(-10, 10)])
for coord in coords:
    entities.append(Dots(coord[0], coord[1], coord[2]))







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

