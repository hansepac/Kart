import pygame as pg
from numpy import array, pi
import numpy as np
from entities.Terrain import TerrainDynamic
from entities.LocalPlayer import LocalPlayer


class MapMaster:
    def __init__(self, terrainDynamicCoordinator, screen, track_origin = np.array([0, 0, 0]), num_flags = 12):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.items = []
        self.terrainDynamicCoordinator = terrainDynamicCoordinator

        self.screen = screen

        # create flags
        self.flags = [track_origin]
        self.num_flags = num_flags
        phi = np.random.uniform(-np.pi, np.pi)
        for _ in range(num_flags):
            # rotate, move, and add a new flag
            phi += np.random.uniform(-np.pi/2, np.pi/2)
            r = np.random.uniform(3, 8)
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
      


    def draw(self, clock):        

        # get tile dimensions
        x_size, y_size = self.screen.get_size()
        x_size = x_size // 2 if len(self.local_players) > 1 else x_size
        y_size = y_size // 2 if len(self.local_players) > 2 else y_size 

        for i, player in enumerate(self.local_players):
            player.render_player_view(clock)
            self.screen.blit(player.screen, ((i % 2)*x_size, (i // 2)*y_size))



    def createTerrainDynamic(self, pos=np.array([0.0, 0.0, 0.0])):

        # creates a terrain dynamic. The driver class uses this. 
        return TerrainDynamic(coordinator=self.terrainDynamicCoordinator, center=pos)
    
    def addLocalPlayer(self, pos=np.array([0.0, 0.0, 0.0]), direction_unitvec=np.array([1.0, 0.0, 0.0]), is_controller=False):
        # calculate screen tile sizes
        x_size, y_size = self.screen.get_size()
        x_size = x_size // 2 if len(self.local_players) + 1 > 1 else x_size
        y_size = y_size // 2 if len(self.local_players) + 1 > 2 else y_size

        new_local_player = LocalPlayer(self, pg.Surface((x_size, y_size)), pos=pos, direction_unitvec=direction_unitvec, is_controller=is_controller)
        
        self.local_players.append(new_local_player)
        self.drivers.append(new_local_player)
        
        # create new screens for other local players
        for player in self.local_players:
            player.screen = pg.Surface((x_size, y_size))
            player.camera.nx = x_size
            player.camera.ny = y_size
            player.camera.updateVpMat()
            print(x_size, y_size)

        
            

        