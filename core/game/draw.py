from __init__ import screen, camera, entities, keyboard
from pygame import gfxdraw as dr
import pygame as pg

def draw():
    # Clear Screen
    screen.fill((0,0,0))

    # Draw all entities
    for entity in entities:
        entity_pos = camera.getScreenCoords([entity.get_pos()])[0]
        # entity.size = entity_pos[2]
        if entity_pos[0] < camera.nx and entity_pos[0] > 0 and entity_pos[1] < camera.ny and entity_pos[1] > 0:
            entity.draw(screen, round(entity_pos[0]), round(entity_pos[1]))
