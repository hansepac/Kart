from utils.cores import Core
from ui import MenuCore

def update(c: Core, mc: MenuCore):
    if c.gameState == c.gameState.TITLE:
        button_click = mc.titleScreen.update(c.events, c.dt)
        if button_click:
            c.gameState = button_click["value"]
    elif c.gameState == c.gameState.JOIN:
        button_click = mc.onlineModeGameScreen.update(c.events, c.dt)
        if button_click:
            c.gameState, c.onlineState = button_click["value"]
    elif c.gameState == c.gameState.CONTROLS:
        c = mc.controllerScreen.update(c)
    return c