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
FRAME_RATE = 120
CAMERA_SCALE = 60
DEBUG = True

# Init game clock
clock = pg.time.Clock()

# Get window size
window_x, window_y = screen.get_size()

# Game States
from utils.states import GameState, OnlineState, GameDebugState
gameState = GameState(0) # {0: TITLE, 1: CHAR_SELEC, 2: IN_GAME, 3: SETTINGS}
onlineState = OnlineState(1) # {0: LOCAL, 1: ONLINE}

# Init Title Screen
from ui import TitleScreen
titleScreen = TitleScreen(screen, gameState, window_x, window_y)

# Camera
from entities import Camera
from numpy import pi
camera = Camera(y=5, z = 0, theta = 0, phi = pi/2, nx = window_x, ny = window_y)

# MapMaster
from entities import MapMaster
mapMaster = MapMaster(screen=screen)
mapMaster.addLocalPlayer()
# mapMaster.addLocalPlayer(is_controller=True)




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

