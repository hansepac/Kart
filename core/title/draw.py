# from ui import MenuCore

def draw(c, mc):
    if c.gameState == c.gameState.TITLE:
        mc.titleScreen.draw()
    elif c.gameState == c.gameState.JOIN:
        mc.onlineModeGameScreen.draw()
    elif c.gameState == c.gameState.CONTROLS:
        mc.controllerScreen.draw()