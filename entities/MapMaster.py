import pygame as pg
from numpy import array, pi
import numpy as np
from utils.ui import draw_debug_text

from entities.Renderable import DriverSprite, TerrainTriangle

class MapMaster:
    def __init__(self):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.items = []
        self.terrain = None

    def get_track_pos(self, pos):
        pos[1] = self.terrain.get_ground_height(pos)
        return pos
    
    def get_track_normal(self, pos):
        return array([0, 1, 0])


    def update(self, events, DEBUG):
        for driver in self.drivers:
            driver.control(events)
            driver.updatePosition()
            driver.pos = self.get_track_pos(driver.pos)
            driver.normal = self.get_track_normal(driver.pos)
        for player in self.local_players:
            player.updateCameraPositon()

      

    def draw(self, screen, clock):
        for player in self.local_players:
            angle = (player.camera.theta + pi/2)/pi
            screen.fill((0, round(angle*200), round(angle*255)))

            # iterate through players is iterating through cameras. 
            player.camera.updateCamMat() # update camera matrices once per frame

            # make renderables
            all_renderables = []

            # add drivers (including this one)
            for driver in self.drivers:
                all_renderables.append(DriverSprite(driver, player.camera))

            # add a renderable for each triangle
            for i in range(len(self.terrain.homo_triangles)):
                all_renderables.append(TerrainTriangle(self.terrain.homo_triangles[i], player.camera, colour=self.terrain.colours_triangles[i])) # creating renderables calculates screen location
            # sort renderables according to depth
            all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

            # now draw renderables
            for renderable in all_renderables:
                renderable.draw(screen)
           
            # draw debug text
            if player.gameDebugState != player.gameDebugState.NORMAL:
                debug_text = [
                    f"Camera Pos: {round(player.camera.x, 2)}, {round(player.camera.y, )}, {round(player.camera.z, 2)}",
                    f"Camera Angle: {player.camera.phi}, {player.camera.theta}",
                    f"FPS: {round(clock.get_fps(), 2)}",
                    f"Debug State: {player.gameDebugState.name}",
                ]
                draw_debug_text(screen, debug_text, (255, 255, 255))




        