from utils.cores import Core
from ui import MenuCore

def update(c: Core, mc: MenuCore):
    if c.gameState == c.gameState.TITLE:
        c = mc.titleScreen.update(c)
    elif c.gameState == c.gameState.JOIN:
        c = mc.onlineModeGameScreen.update(c)
    elif c.gameState == c.gameState.CONTROLS:
        c = mc.controllerScreen.update(c)
    return c