import pygame as pg
from numpy import array, sin, cos, pi

class MapMaster:
    def __init__(self):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.entities = []
        self.items = []

    def get_track_pos(self, pos):
        pos[1] = 0.1 * ( pos[0] ** 2 + pos[2] ** 2 )
        return pos
    
    def get_track_normal(self, pos):
        return array([-2*pos[0], 1, -2*pos[2]], dtype=float)

    def update(self, screen):
        win_x, win_y = screen.get_size()
        for driver in self.drivers:
            driver.control()
            driver.updatePosition()
            driver.pos = self.get_track_pos(driver.pos)
            driver.normal = self.get_track_normal(driver.pos)
        for player in self.local_players:
            player.updateCameraPositon(win_x, win_y)

        # for entity in self.entities:
        #     entity.update()
        # for item in self.items:
        #     item.update()

    def draw(self, screen):
        for player in self.local_players:
            # Draw Drivers
            driver_pos = [driver.get_pos() for driver in self.drivers]
            driver_screen_pos = player.camera.getScreenCoords(driver_pos)
            for i in range(len(self.drivers)):
                if driver_screen_pos[i] is not None:
                    self.drivers[i].draw(screen, round(driver_screen_pos[i][0]), round(driver_screen_pos[i][1]))
            # Draw Dots
            dot_pos = [entity.get_pos() for entity in self.entities]
            dot_screen_pos = player.camera.getScreenCoords(dot_pos)
            for i in range(len(self.entities)):
                if dot_screen_pos[i] is not None:
                    self.entities[i].draw(screen, round(dot_screen_pos[i][0]), round(dot_screen_pos[i][1]))
        