from __init__ import mapMaster, DEBUG


def update(events, dt, gameState):
    # camera.control()
    mapMaster.update(events, dt, DEBUG)
    return gameState


