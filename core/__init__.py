from . import title
from . import game
from .update import update
from .draw import draw

from __init__ import screen, gameState, onlineState, window_x, window_y
from ui import TitleScreen, JoinGameScreen
titleScreen = TitleScreen(screen, gameState, window_x, window_y)
joinGameScreen = JoinGameScreen(screen, gameState, onlineState, window_x, window_y)