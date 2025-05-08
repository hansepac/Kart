import pygame as pg
import numpy as np
from entities.Terrain import TerrainDynamic
from entities.LocalPlayer import LocalPlayer
from entities.Terrain import TerrainDynamicCoordinator
from entities.Driver import Driver
from entities.AIDriver import AIDriver
from utils.states import GameState

class MapMaster:
    def __init__(self, screen, is_server = False):
        self.drivers = []
        self.alien_drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.items = []
        self.terrainDynamicCoordinator = self.terrainDynamicCoordinator=TerrainDynamicCoordinator(radius=20)
        self.screen = screen
        self.is_server = is_server
        self.map_loaded = False
        if is_server:
            self.setup_game()

        self.completed_drivers = []

        

    def setup_game(self, track_origin = np.array([0, 0, 0]), num_flags = 12):
        # Create Flags
        self.flags = [track_origin]
        self.num_flags = num_flags
        phi = np.random.uniform(-np.pi, np.pi)
        for _ in range(num_flags - 1):
            # rotate, move, and add a new flag
            phi += np.random.uniform(-np.pi/2, np.pi/2)
            r = np.random.uniform(3, 8)
            new_flag_pos = self.flags[-1] + r*np.array([np.cos(phi), 0, np.sin(phi)])
            new_flag_pos[1] = self.terrainDynamicCoordinator.get_rough_height(new_flag_pos) # put it on the ground 
            self.flags.append(new_flag_pos)
        self.map_loaded = True

    def get_game_setup_json(self):
        # returns a json object with game information
        return {
            "flags": [flag.tolist() for flag in self.flags],
            "num_flags": self.num_flags
        }
    
    def get_game_data(self):
        return {
            "drivers": [driver.get_data() for driver in self.drivers if not driver.is_alien],
        }
    
    def overwrite_game_setup(self, game_info_json):
        # overwrites the game info with the given json object
        self.flags = game_info_json["flags"]
        self.num_flags = game_info_json["num_flags"]

    def update_from_server(self, server_game_data_chunks):
        # Update driver positions from server
        for server_game_data in server_game_data_chunks:
            dat = server_game_data["dat"]
            if server_game_data["msg_type"] == "live_data":
                for key, value in dat.items():
                    if key == "drivers":
                        for driver_data in value:
                            new_driver = True
                            for driver in self.drivers:
                                if driver.id == driver_data["id"] and driver.is_alien:
                                    driver.update_from_server(driver_data)
                                    new_driver = False
                                    break
                                elif driver.id == driver_data["id"]:
                                    new_driver = False
                                    break
                            if new_driver:
                                new_driver = Driver(self, pos=driver_data["pos"], direction_unitvec=driver_data["direction_unitvec"], id=driver_data["id"], is_alien=True)
                                new_driver.update_from_server(driver_data)
                                self.drivers.append(new_driver)

            elif server_game_data["msg_type"] == "game_setup":
                print("OVERWRITING GAME SETUP")
                self.overwrite_game_setup(dat["game_setup"])
                self.terrainDynamicCoordinator.overwrite_seed(dat["seed"])

    def update(self, c):
        # Update local player / driver positions
        driver_dat = []
        for driver in self.drivers:
            if driver.is_alien:
                continue
            else:
                driver.terrainDynamic.update_grid(driver.pos)
                driver.control()
                driver.updatePosition(c.dt)
                driver_dat.append(driver.get_data())

                # check for flag indices
                if np.linalg.norm(driver.pos - self.flags[driver.flag_index]) < 0.2:
                    if driver.flag_index >= self.num_flags - 1:
                        if not driver.completed:
                            driver.completed = True
                            self.completed_drivers.append(driver)

                            if len(self.completed_drivers) == len(self.drivers):
                                c.gameState = GameState(0)
                                pg.mouse.set_visible(True)
                                c.soundmaster.clear_game_sounds()
                    else:
                        driver.flag_index += 1

        for player in self.local_players:
            player.updateCameraPositon()

        self.sortPlayers()
      
    def draw(self, c):        

        # get tile dimensions
        x_size, y_size = self.screen.get_size()
        x_size = x_size // 2 if len(self.local_players) > 1 else x_size
        y_size = y_size // 2 if len(self.local_players) > 2 else y_size 

        sound_drivers = 0
        sound_idlers = 0
        for i, player in enumerate(self.local_players):
            player.render_player_view(c.clock)
            self.screen.blit(player.screen, ((i % 2)*x_size, (i // 2)*y_size))
            
            # get sound stuff 
            if player.inputs["gas"]:
                sound_drivers += 1
                if player.last_go_state == False:
                    c.soundmaster.go_hit.play()
                    player.last_go_state = True
            else:
                player.last_go_state = False
                sound_idlers += 1

            if player.inputs["drift"]:
                if player.last_drift_state == False:
                    c.soundmaster.drifting_hit.play()
                    player.last_drift_state = True 
            else:
                player.last_drift_state = False

        c.soundmaster.drive_sound_count = sound_drivers
        c.soundmaster.idle_sound_count = sound_idlers
        c.soundmaster.check_runtime_sounds()


        # Draw scoreboard:
        font = pg.font.SysFont("papyrus", 24)
        padding = 20
        text_color = (255, 255, 255)
        bg_color = (50, 50, 50, 150)  # RGBA: dark gray with alpha 150 (out of 255)

        for i, driver in enumerate(self.completed_drivers):
            text_str = f"{i + 1}. {driver.name}"
            text_surf = font.render(text_str, True, text_color)
            text_rect = text_surf.get_rect()
            text_rect.topright = (self.screen.get_width() - padding, padding + i * 30)

            # Create transparent background box
            box_surf = pg.Surface((text_rect.width + 10, text_rect.height + 4), pg.SRCALPHA)
            box_surf.fill(bg_color)

            # Blit box, then text
            self.screen.blit(box_surf, (text_rect.right - box_surf.get_width(), text_rect.top - 2))
            self.screen.blit(text_surf, text_rect)
        



    def createTerrainDynamic(self, pos=np.array([0.0, 0.0, 0.0])):

        # creates a terrain dynamic. The driver class uses this. 
        return TerrainDynamic(coordinator=self.terrainDynamicCoordinator, center=pos)
    
    def addLocalPlayer(self, controller, pos=np.array([0.0, 0.0, 0.0]), direction_unitvec=np.array([1.0, 0.0, 0.0]), car_sprite = 0):
        # calculate screen tile sizes
        x_size, y_size = self.screen.get_size()
        x_size = x_size // 2 if len(self.local_players) + 1 > 1 else x_size
        y_size = y_size // 2 if len(self.local_players) + 1 > 2 else y_size

        # Create LocalPlayer
        new_local_player = LocalPlayer(self, pg.Surface((x_size, y_size)), pos=pos, direction_unitvec=direction_unitvec, controller=controller, car_sprite=car_sprite)
        
        # create new screens for other local players
        for player in self.local_players:
            player.screen = pg.Surface((x_size, y_size))
            player.camera.nx = x_size
            player.camera.ny = y_size
            player.camera.updateVpMat()

        self.local_players.append(new_local_player)
        self.drivers.append(new_local_player)
        
    def addAIPlayer(self, pos=np.array([0.0, 0.0, 0.0]), direction_unitvec=np.array([1.0, 0.0, 0.0]), car_sprite = 2):
        self.drivers.append(AIDriver(self, pos=pos, direction_unitvec=direction_unitvec, car_sprite=car_sprite))


    def sortPlayers(self):
        self.drivers = sorted(self.drivers,
                                key=lambda d: (
                                    -d.flag_index,
                                    np.linalg.norm(d.pos - self.flags[d.flag_index])
                                )
                            )
        for i in range(len(self.drivers)):
            self.drivers[i].rank = i + 1

        