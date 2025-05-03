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
        self.terrainGrid = None


    def update(self, events, DEBUG):
        for driver in self.drivers:
            driver.control(events)
            driver.updatePosition()
        for player in self.local_players:
            player.updateCameraPositon()

      

    def draw(self, screen, clock):
        for player in self.local_players:
            angle = (player.camera.theta + pi/2)/pi
            sky_color = (0, round(angle*200), round(angle*255))
            screen.fill(sky_color)

            # iterate through players is iterating through cameras. 
            player.camera.updateCamMat() # update camera matrices once per frame

            # make renderables
            all_renderables = []

            # add drivers (excluding this one)
            for driver in self.drivers:
                if player != driver:
                    all_renderables.append(DriverSprite(driver, player.camera))

            # add a renderable for each triangle
            for terrain_tile in self.terrainGrid.get_adjacent_tiles(player.pos, player.direction_unitvec):
                for i in range(len(terrain_tile.homo_triangles)):
                    all_renderables.append(TerrainTriangle(terrain_tile.homo_triangles[i], player.camera, colour=terrain_tile.colours_triangles[i], skycolour=sky_color)) # creating renderables calculates screen location
                
            # sort renderables according to depth
            all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

            # now draw renderables
            for renderable in all_renderables:
                renderable.draw(screen)

            # now do this player last
            DriverSprite(player, player.camera).draw(screen)
           
            # draw debug text
            if player.gameDebugState != player.gameDebugState.NORMAL:
                debug_text = [
                    f"Camera Pos: {round(player.camera.x, 2)}, {round(player.camera.y, )}, {round(player.camera.z, 2)}",
                    f"Camera Angle: {round(player.phi, 1)}, {round(player.camera.phi, 1)}",
                    f"Theta Diff: {round(min(player.phi - player.camera.phi, player.phi - player.camera.phi + 2*np.pi, player.phi - player.camera.phi - 2*np.pi, key=abs), 2)}",
                    f"FPS: {round(clock.get_fps(), 2)}",
                    f"Debug State: {player.gameDebugState.name}",
                    f"Is on Ground: {player.is_on_ground}",
                    f"x: {round(player.speed)}",
                    f"f(x): {round(player.get_speed(player.speed), 2)}",
                    f"slope_force: {round(player.slope_speed, 2)}",
                    f"y_velocity: {round(player.vel_y, 2)}"
                ]
                draw_debug_text(screen, debug_text, (255, 255, 255))




        