from __init__ import window, player
from pygame import gfxdraw as dr
import pygame as pg

def draw():
    # Clear Screen
    window.fill((0,0,0))

    # Draw all entities
    player.draw(window)