import pygame as pg
from numpy import array, pi
import numpy as np
from ui import draw_debug_text, draw_speedometer, show_keyboard_ui, draw_minimap
from entities.Terrain import TerrainDynamic

from entities.Renderable import *

class MapMaster:
    def __init__(self, terrainDynamicCoordinator, track_origin = np.array([0, 0, 0]), num_flags = 12):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.items = []
        self.terrainDynamicCoordinator = terrainDynamicCoordinator

        # create flags
        self.flags = [track_origin]
        self.num_flags = num_flags
        phi = np.random.uniform(-np.pi, np.pi)
        for _ in range(num_flags):
            # rotate, move, and add a new flag
            phi += np.random.uniform(-np.pi/2, np.pi/2)
            r = np.random.uniform(1, 8)
            new_flag_pos = self.flags[-1] + r*np.array([np.cos(phi), 0, np.sin(phi)])
            new_flag_pos[1] = self.terrainDynamicCoordinator.get_rough_height(new_flag_pos) # put it on the ground 
            self.flags.append(new_flag_pos)


    def update(self, events, dt, DEBUG):
        for driver in self.drivers:
            driver.control(events)
            driver.updatePosition(dt)

            # check for flag indices
            if np.linalg.norm(driver.pos - self.flags[driver.flag_index]) < 0.2:
                driver.flag_index += 1

        for player in self.local_players:
            player.terrainDynamic.update_grid(player.pos)
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
            for i in range(len(player.terrainDynamic.homo_triangles)):
                all_renderables.append(TerrainTriangle(player.terrainDynamic.homo_triangles[i], player.camera, colour=player.terrainDynamic.colours_triangles[i], skycolour=sky_color)) # creating renderables calculates screen location
                
            # add flag renderable
            for i in range(self.num_flags):
                all_renderables.append(FlagSprite(self.flags[i], player.camera, isCurrent=(player.flag_index == i)))

            # sort renderables according to depth
            all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

            # now draw renderables
            for renderable in all_renderables:
                renderable.draw(screen)

            # now do this player last
            DriverSprite(player, player.camera).draw(screen)

            window_x, window_y = screen.get_size()
            radius = 100
            draw_speedometer(screen, abs(player.speed/10), (radius+30,radius+30), radius=radius, max_val=player.max_momentum/10, tick_step=10)
            show_keyboard_ui(screen, (window_x-350, window_y-350))
            
            displacement_unit_vec = np.array([self.flags[player.flag_index][0], self.flags[player.flag_index][2]]) - np.array([player.pos[0], player.pos[2]])
            displacement_unit_vec /= np.linalg.norm(displacement_unit_vec)
            direction_2d = np.array([player.direction_unitvec[0], player.direction_unitvec[2]])
            direction_2d /= np.linalg.norm(direction_2d)
            angle_between = np.arccos(direction_2d @ displacement_unit_vec)
            
            draw_minimap(screen, angle_between, (radius+30,3*radius+60), radius=80)
           
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
                    f"y_velocity: {round(player.vel_y, 2)}",
                    f"Flag screen depth: {FlagSprite(self.flags[player.flag_index], player.camera).screen_depth}"
                ]
                draw_debug_text(screen, debug_text, (255, 255, 255))

            else:
                debug_text = [
                    f"FPS: {round(clock.get_fps(), 2)}"
                ]
                draw_debug_text(screen, debug_text, (255, 255, 255))


    def createTerrainDynamic(self, pos=np.array([0, 0, 0])):
        # creates a terrain dynamic. The driver class uses this. 
        return TerrainDynamic(coordinator=self.terrainDynamicCoordinator, center=pos)

        