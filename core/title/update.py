import core

def update(events, dt, gameState, onlineState):
    if gameState == gameState.TITLE:
        gameState = core.titleScreen.update(events, dt, gameState)
    elif gameState == gameState.JOIN:
        gameState, onlineState = core.joinGameScreen.update(events, dt, (gameState, onlineState))

    return gameState, onlineState