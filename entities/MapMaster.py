import pygame as pg
from numpy import array, pi
import numpy as np
from utils.ui import draw_debug_text

class MapMaster:
    def __init__(self):
        self.drivers = []
        self.local_players = []
        self.player_screen_dimensions = []
        self.entities = []
        self.items = []
        self.track = None

    def get_track_pos(self, pos):
        pos[1] = self.track.get_ground_height(pos)
        return pos
    
    def get_track_normal(self, pos):
        return array([0, 1, 0])

    def update(self, screen, events, DEBUG):
        win_x, win_y = screen.get_size()
        for driver in self.drivers:
            driver.control(events)
            driver.updatePosition()
            driver.pos = self.get_track_pos(driver.pos)
            driver.normal = self.get_track_normal(driver.pos)
        for player in self.local_players:
            player.updateCameraPositon(win_x, win_y)

        # for entity in self.entities:
        #     entity.update()
        # for item in self.items:
        #     item.update()

    def draw(self, screen, clock):
        for player in self.local_players:
            angle = (player.camera.theta + pi/2)/pi
            screen.fill((0, round(angle*200), round(angle*255)))
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
            
            for edge in self.track.track_edge_homocoords:
                screenedgecoords = player.camera.getScreenCoords(edge)
                if np.linalg.norm(screenedgecoords[0]) > 1 and np.linalg.norm(screenedgecoords[1]) > 1:
                    pg.draw.line(screen, (255,255,255), list(screenedgecoords[0][0:2]), list(screenedgecoords[1][0:2]), 1)

            for rect in self.track.track_rect_homocoords:
                src = player.camera.getScreenCoords(rect)
                if np.linalg.norm(src[0]) > 1 and np.linalg.norm(src[1]) > 1 and np.linalg.norm(src[2]) > 1 and np.linalg.norm(src[3]) > 1:
                    pg.draw.polygon(screen, (255, 228, 168), [src[0][0:2], src[1][0:2], src[2][0:2], src[3][0:2]])

            if player.gameDebugState != player.gameDebugState.NORMAL:
                debug_text = [
                    f"Camera Pos: {round(player.camera.x, 2)}, {round(player.camera.y, )}, {round(player.camera.z, 2)}",
                    f"Camera Angle: {player.camera.phi}, {player.camera.theta}",
                    f"FPS: {round(clock.get_fps(), 2)}",
                    f"Debug State: {player.gameDebugState.name}",
                ]
                draw_debug_text(screen, debug_text, (255, 255, 255))




        

        