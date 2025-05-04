from utils.cores import Core
from ui import MenuCore

def update(c: Core, mc: MenuCore):
    if c.gameState == c.gameState.TITLE:
        c.gameState = mc.titleScreen.update(c.events, c.dt, c.gameState)
    elif c.gameState == c.gameState.JOIN:
        c.gameState, c.onlineState = mc.joinGameScreen.update(c.events, c.dt, (c.gameState, c.onlineState))
    return c