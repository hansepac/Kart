from __init__ import gameState
import core.title as title
import core.game as game

def update():
    # Run updates based on gameState
    if gameState == gameState.TITLE:
        title.update()
    elif gameState == gameState.IN_GAME:
        game.update()