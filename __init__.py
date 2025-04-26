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
pg.mouse.set_visible(False)
pg.event.set_grab(True) 

# Example
window_x, window_y = screen.get_size()

# Camera
from entities import Camera
from numpy import pi
camera = Camera(z = -10, theta = 0, phi = pi/2, nx = window_x, ny = window_y)

# MapMaster
from entities import MapMaster
mapMaster = MapMaster()


# Create Dots
from entities import Dots
entities = []
coords = []

from random import randint, random
for i in range(10000):
    x = random() * 20 - 10
    z = random() * 20 - 10
    coords.append([x, 0.1 * ( x ** 2 + z ** 2 ) , z])
for coord in coords:
    entities.append(Dots(coord[0], coord[1], coord[2]))

mapMaster.entities = entities
from entities import LocalPlayer
local_player = LocalPlayer()
mapMaster.local_players.append(local_player)
mapMaster.drivers.append(local_player)









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

