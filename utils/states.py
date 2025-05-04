from enum import Enum

class GameState(Enum):
    TITLE = 0
    CHAR_SELECT = 1
    IN_GAME = 2
    SETTINGS = 3

class OnlineState(Enum):
    LOCAL = 0
    ONLINE = 1

class GameDebugState(Enum):
    NORMAL = 0
    DRIVER_DEBUG = 1
    FLY_DEBUG = 2
