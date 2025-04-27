from __init__ import gameState
import core.title as title
import core.game as game

def update(events):
    # Get all the latest key presses
    # Run updates based on gameState
    if gameState == gameState.TITLE:
        title.update(events)
    elif gameState == gameState.IN_GAME:
        game.update(events)