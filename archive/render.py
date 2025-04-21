import numpy as np
import pygame,sys
from pygame import *

WIDTH = 480
HEIGHT = 480
WHITE = (255,255,255) #RGB
BLACK = (0,0,0) #RGB
FOV = 90
n = 5
f = 30


np.matrix([[1/((WIDTH/HEIGHT)*np.tan(FOV/2)),0,0,0],
           [0,1/np.tan(FOV/2),0,0],
           [0,0,f/(f-n),-f*n/(f-n)],
           [0,0,1,0]])

point = np.array([0,0,20,1])
camera = np.array([0,0,0,1])
look_dir = np.array([0,0])


pygame.init()
screen = display.set_mode((WIDTH,HEIGHT),0,32)
display.set_caption("Name of Application")
screen.fill(WHITE)
timer = pygame.time.Clock()
pos_on_screen, radius = (50, 50), 20    
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    timer.tick(60) #60 times per second you can do the math for 17 ms
    draw.circle(screen, BLACK, pos_on_screen, radius)
    display.update()