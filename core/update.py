import core.title as title
import core.game as game

def update(events, dt, gameState):
    if gameState == gameState.TITLE:
        gameState = title.update(events, dt, gameState)
    elif gameState == gameState.IN_GAME:
        gameState = game.update(events, dt, gameState)
    return gameState