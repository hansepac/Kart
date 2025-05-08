from core import title
from core import game
from utils.cores import Core
from ui import MenuCore

def draw(c: Core, mc: MenuCore):
    if c.gameState != c.gameState.IN_GAME:
        title.draw(c, mc)
    elif c.gameState == c.gameState.IN_GAME:
        game.draw(c)
