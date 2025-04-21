from __init__ import gameState
from core import title
from core import game

def draw():
    if gameState == gameState.TITLE:
        title.draw()
    elif gameState == gameState.IN_GAME:
        game.draw()
