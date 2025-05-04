from utils.cores import Core
from ui import MenuCore

def draw(c: Core, mc: MenuCore):
    if c.gameState == c.gameState.TITLE:
        mc.titleScreen.draw()
    elif c.gameState == c.gameState.JOIN:
        mc.joinGameScreen.draw()