from __init__ import gameState, keyboard
import core.title as title
import core.game as game

def update():
    # Get all the latest key presses
    keyboard.update()
    # Run updates based on gameState
    if gameState == gameState.TITLE:
        title.update()
    elif gameState == gameState.IN_GAME:
        game.update()