#%%
import numpy as np

WIDTH = 480
HEIGHT = 480
WHITE = (255,255,255) #RGB
BLACK = (0,0,0) #RGB
FOV = 90
n = 5
f = 30

V = np.matrix([[1/((WIDTH/HEIGHT)*np.tan(FOV/2)),0,0,0],
           [0,1/np.tan(FOV/2),0,0],
           [0,0,f/(f-n),-f*n/(f-n)],
           [0,0,1,0]])

point = np.array([10,10,10,1])
camera = np.array([0,0,0,1])
look_dir = np.array([0,0])

V@point
# %%
