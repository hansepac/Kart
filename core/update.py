import core.title as title
import core.game as game
import core

from utils.cores import Core, GameCore
from ui import MenuCore
from entities import MapMaster
from Server import Client

def update(c: Core, mc: MenuCore):
    global gc
    if c.gameState != c.gameState.IN_GAME:
        c = title.update(c, mc)
        if c.gameState == c.gameState.IN_GAME:
            core.gc = core.game_init(c)
    elif c.gameState == c.gameState.IN_GAME:
        c = game.update(c, core.gc)
    return c