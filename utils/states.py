from enum import Enum

class GameState(Enum):
    TITLE = 0
    JOIN = 1
    CHAR_SELECT = 2
    IN_GAME = 3
    CONTROLS = 4

class GameDebugState(Enum):
    NORMAL = 0
    DRIVER_DEBUG = 1
    FLY_DEBUG = 2

class OnlineState(Enum):
    LOCAL = 0
    CLIENT = 1
    HOST = 2

