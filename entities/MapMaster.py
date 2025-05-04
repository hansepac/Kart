import pygame as pg
from numpy import array, pi
import numpy as np
from entities.Terrain import TerrainDynamic
from entities.LocalPlayer import LocalPlayer
from entities.Terrain import TerrainDynamicCoordinator
from entities.Driver import Driver

class MapMaster:
    def __init__(self, screen, is_server = False):
        self.drivers = []
        self.alien_drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.items = []
        self.terrainDynamicCoordinator = self.terrainDynamicCoordinator=TerrainDynamicCoordinator(grid_spacing=0.1)
        self.screen = screen
        self.is_server = is_server
        if is_server:
            self.setup_game()

    def setup_game(self, track_origin = np.array([0, 0, 0]), num_flags = 12):
        # Create Flags
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

    def get_game_setup_json(self):
        # returns a json object with game information
        return {
            "flags": [flag.tolist() for flag in self.flags],
            "num_flags": self.num_flags
        }
    
    def get_game_data(self):
        return {
            "drivers": [driver.get_data() for driver in self.drivers]
        }
    
    def overwrite_game_setup(self, game_info_json):
        # overwrites the game info with the given json object
        self.flags = game_info_json["flags"]
        self.num_flags = game_info_json["num_flags"]

    def update_from_server(self, server_game_data_chunks):
        # Update driver positions from server
        for server_game_data in server_game_data_chunks:
            for key, value in server_game_data.items():
                if key == "live_data":
                    for key2, value2 in value.items():
                        if key2 == "drivers":
                            for driver_data in value2:
                                new_driver = True
                                for driver in self.drivers:
                                    if driver.id == driver_data["id"]:
                                        driver.update_from_server(driver_data)
                                        new_driver = False
                                        break
                                if new_driver:
                                    new_driver = Driver(self, pos=driver_data["pos"], direction_unitvec=driver_data["direction_unitvec"], id=driver_data["id"])
                                    new_driver.update_from_server(driver_data)
                                    self.drivers.append(new_driver)

                elif key == "game_setup":
                    self.overwrite_game_setup(value["game_setup"])
                    self.terrainDynamicCoordinator.overwrite_seed(value["seed"])

    def update(self, c):
        # Update local player / driver positions
        driver_dat = []
        for driver in self.drivers:
            if driver.is_alien:
                continue
            else:
                driver.control(c.events)
                driver.updatePosition(c.dt)
                driver_dat.append(driver.get_data())

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

        # Create LocalPlayer
        new_local_player = LocalPlayer(self, pg.Surface((x_size, y_size)), pos=pos, direction_unitvec=direction_unitvec, is_controller=is_controller)
        
        # create new screens for other local players
        for player in self.local_players:
            player.screen = pg.Surface((x_size, y_size))
            player.camera.nx = x_size
            player.camera.ny = y_size
            player.camera.updateVpMat()

        self.local_players.append(new_local_player)
        self.drivers.append(new_local_player)
        
        

        
            

        