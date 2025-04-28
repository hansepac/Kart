import pygame as pg
from numpy import array
import numpy as np

from entities.Renderable import DriverSprite, TerrainTriangle

class MapMaster:
    def __init__(self):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.entities = []
        self.items = []
        self.terrain = None

    def get_track_pos(self, pos):
        pos[1] = self.terrain.get_ground_height(pos)
        return pos
    
    def get_track_normal(self, pos):
        return array([0, 1, 0])

    def update(self):
        for driver in self.drivers:
            driver.control()
            driver.updatePosition()
            driver.pos = self.get_track_pos(driver.pos)
            driver.normal = self.get_track_normal(driver.pos)
        for player in self.local_players:
            player.updateCameraPositon()

        # for entity in self.entities:
        #     entity.update()
        # for item in self.items:
        #     item.update()

    def draw(self, screen):
        for player in self.local_players:
            # iterate through players is iterating through cameras. 
            player.camera.updateCamMat() # update camera matrices once per frame

            # make renderables
            all_renderables = []

            # add drivers (including this one)
            for driver in self.drivers:
                all_renderables.append(DriverSprite(driver, player.camera))

            # add a renderable for each triangle
            for triangle in self.terrain.homo_triangles:
                all_renderables.append(TerrainTriangle(triangle, player.camera)) # creating renderables calculates screen location
            # sort renderables according to depth
            all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

            # now draw renderables
            for renderable in all_renderables:
                renderable.draw(screen)
           
                
                    
                    
                

        

        