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

# INITIALIZE FRAME RATE STUFF
clock = pg.time.Clock()

# Game States
from utils.states import GameState, OnlineState, GameDebugState
gameState = GameState(1) # {0: TITLE, 1: IN_GAME}
onlineState = OnlineState(1) # {0: LOCAL, 1: ONLINE}

# Keyboard
pg.mouse.set_visible(False)
pg.event.set_grab(True) 

# Camera
from entities import Camera
from numpy import pi
window_x, window_y = screen.get_size()
camera = Camera(y=5, z = 0, theta = 0, phi = pi/2, nx = window_x, ny = window_y)

# MapMaster
from entities import MapMaster
mapMaster = MapMaster()

# Create Dots
from entities import Dots
entities = []
coords = []

from entities import Track
firsttrack = Track(tracktype = Track.TRACK_TYPE_FLAT)
for coord in firsttrack.track_verts_homocoords:
    entities.append(Dots(coord[0], coord[1], coord[2]))
entities[0].color = (0, 255, 0)
entities[1].color = (0, 255, 0)
entities[2].color = (0, 255, 0)
entities[3].color = (0, 0, 255)
entities[4].color = (0, 0, 255)
entities[5].color = (0, 0, 255)

mapMaster.entities = entities
from entities import LocalPlayer
local_player = LocalPlayer()
mapMaster.local_players.append(local_player)
mapMaster.drivers.append(local_player)
mapMaster.track = firsttrack






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

