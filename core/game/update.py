from __init__ import camera, mapMaster, screen, DEBUG


def update(events, dt):
    # camera.control()
    mapMaster.update(events, dt, DEBUG)


