from __init__ import screen, player
from pygame import gfxdraw as dr
import pygame as pg

def draw():
    # Clear Screen
    screen.fill((0,0,0))

    # Draw all entities
    player.draw(screen)