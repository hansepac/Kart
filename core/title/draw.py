import core

def draw(gameState):
    if gameState == gameState.TITLE:
        core.titleScreen.draw()
    elif gameState == gameState.JOIN:
        core.joinGameScreen.draw()