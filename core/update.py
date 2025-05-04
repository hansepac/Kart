from __init__ import screen
import core.title as title
import core.game as game
import core

def update(events, dt, gameState, onlineState):
    if gameState != gameState.IN_GAME:
        gameState, onlineState = title.update(events, dt, gameState, onlineState)
        if gameState == gameState.IN_GAME:
            game.game_init(onlineState)
    elif gameState == gameState.IN_GAME:
        gameState = game.update(events, dt, gameState, onlineState)
    return gameState