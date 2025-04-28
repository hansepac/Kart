from __init__ import camera, mapMaster, screen, DEBUG


def update(events):
    # camera.control()
    mapMaster.update(events, DEBUG)


