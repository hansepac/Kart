import numpy as np
from .Driver import Driver
from .Camera import Camera
from input import Controller
from utils.states import GameDebugState
from ui import draw_debug_text, draw_speedometer, show_keyboard_ui, draw_minimap
from entities.Renderable import *

class LocalPlayer(Driver):
    # it already has position and velocity stuff

    def __init__(self, mapmaster, player_screen, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0]), is_controller = False, car_sprite = 0):
        super().__init__(mapmaster, pos = pos, direction_unitvec = direction_unitvec, car_sprite=car_sprite)
        self.is_controller = is_controller
        self.controller: Controller = Controller(is_controller)
        self.camera = Camera(*pos, np.atan2(direction_unitvec[2], direction_unitvec[0]), nx = player_screen.get_size()[0], ny = player_screen.get_size()[1])
        self.camera_height = 0.2
        self.camera_distance = 0.3
        self.camera_theta = 0.2
        self.gameDebugState: GameDebugState = GameDebugState(0)

        self.screen = player_screen

    def render_player_view(self, clock):

        angle = (self.camera.theta + np.pi/2)/np.pi
        sky_color = (0, round(angle*200), round(angle*255))
        self.screen.fill(sky_color)

        # iterate through players is iterating through cameras. 
        self.camera.updateCamMat() # update camera matrices once per frame

        # make renderables
        nontriangle_renderables, triangle_renderables = [], []

        # add drivers (excluding this one)
        player_renderable = None
        for driver in self.mapmaster.drivers:
            new_driver_renderable = DriverSprite(driver, self.camera)
            if self == driver:
                player_renderable = new_driver_renderable
            nontriangle_renderables.append(new_driver_renderable)

        # add a renderable for each triangle
        for i in range(len(self.terrainDynamic.homo_triangles)):
            triangle_renderables.append(TerrainTriangle(self.terrainDynamic.homo_triangles[i], self.camera, colour=self.terrainDynamic.colours_triangles[i], skycolour=sky_color)) # creating renderables calculates screen location
            
        # add flag renderable
        for i in range(self.mapmaster.num_flags):
            nontriangle_renderables.append(FlagSprite(self.mapmaster.flags[i], self.camera, isCurrent=(self.flag_index == i), isLast=(i == self.mapmaster.num_flags - 1)))

        # sort renderables according to depth
        all_renderables = calculateRenderableScreenCoords(self.camera, nontriangle_renderables, triangle_renderables)
        all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

        # now draw renderables
        for renderable in all_renderables:
            if renderable is not player_renderable:
                renderable.draw(self.screen)
        player_renderable.draw(self.screen) # draw this player last

        window_x, window_y = self.screen.get_size()
        radius1 = 60
        draw_speedometer(self.screen, abs(self.speed/10), (radius1+30,radius1+30), radius=radius1, max_val=self.max_momentum/10, tick_step=10, name="")
        radius2 = 80
        draw_speedometer(self.screen, self.actual_speed*2500, (2*radius1+60 + radius2, radius1+30), radius=radius2, max_val=100, tick_step=10)
        if not self.is_controller:
            show_keyboard_ui(self.screen, (window_x-350, window_y-350))
        
        # this stuff is termporary for minimap
        displacement_unit_vec = np.array([self.mapmaster.flags[self.flag_index][0], self.mapmaster.flags[self.flag_index][2]]) - np.array([self.pos[0], self.pos[2]])
        phi1 = np.atan2(self.direction_unitvec[2], self.direction_unitvec[0])
        phi2 = np.atan2(displacement_unit_vec[1], displacement_unit_vec[0])
        angle_between = (phi2 - phi1 ) % (2*np.pi)
        
        draw_minimap(self.screen, angle_between, (radius1+30,3*radius1+60), radius=80)
        
        # draw debug text
        if self.gameDebugState != self.gameDebugState.NORMAL:
            debug_text = [
                f"Camera Pos: {round(self.camera.x, 2)}, {round(self.camera.y, )}, {round(self.camera.z, 2)}",
                f"Camera Angle: {round(self.phi, 1)}, {round(self.camera.phi, 1)}",
                f"Theta Diff: {round(min(self.phi - self.camera.phi, self.phi - self.camera.phi + 2*np.pi, self.phi - self.camera.phi - 2*np.pi, key=abs), 2)}",
                f"FPS: {round(clock.get_fps(), 2)}",
                f"Debug State: {self.gameDebugState.name}",
                f"Is on Ground: {self.is_on_ground}",
                f"x: {round(self.speed)}",
                f"f(x): {round(self.get_speed(self.speed), 2)}",
                f"slope_force: {round(self.slope_speed, 2)}",
                f"y_velocity: {round(self.vel_y, 2)}"
            ]
            draw_debug_text(self.screen, debug_text, (255, 255, 255))

        else:
            debug_text = [
                f"FPS: {round(clock.get_fps(), 2)}"
            ]
            draw_debug_text(self.screen, debug_text, (255, 255, 255))


    def updateCameraPositon(self):
        if self.gameDebugState != self.gameDebugState.FLY_DEBUG:
            ground_height = self.terrainDynamic.get_ground_height(np.array([self.camera.x, self.camera.y, self.camera.z]))
            camera_theta_move_rate =  np.clip(self.camera_height/1.5/np.clip(self.camera.y - ground_height, self.camera_height, self.camera_height*10), 0.01, 1)
            camera_phi_offset = min(self.phi - self.camera.phi, self.phi - self.camera.phi + 2*np.pi, self.phi - self.camera.phi - 2*np.pi, key=abs)
            camera_phi_move_rate = np.clip((abs(camera_phi_offset)/np.pi*2), 0.01, 1)
            # TODO: Adjust camera position factoring in the theta angle of ground
            self.camera.theta = (1-camera_theta_move_rate)*self.camera_theta - camera_theta_move_rate * np.atan2(self.camera.y - self.pos[1], self.camera_distance)
            self.camera.phi = self.camera.phi + camera_phi_move_rate * camera_phi_offset
            if self.camera.phi < 0:
                self.camera.phi += 2*np.pi
            if self.camera.phi > 2*np.pi:
                self.camera.phi -= 2*np.pi
            
            horizontal_unitvec = self.direction_unitvec/np.linalg.norm(self.direction_unitvec)
            horizontal_unitvec[1] = 0
            cam_pos = self.pos - self.camera_distance*horizontal_unitvec + np.array([0, 1, 0])*self.camera_height
            self.camera.x = cam_pos[0]
            self.camera.y = (1-camera_theta_move_rate)*self.camera.y + camera_theta_move_rate*(ground_height + self.camera_height)
            self.camera.z = cam_pos[2]

    def updateCameraPositonOld(self):
        if self.gameDebugState != self.gameDebugState.FLY_DEBUG:
            #               TODO: Adjust camera position factoring in the theta angle of ground
            self.camera.theta = -np.atan2(self.camera_height, self.camera_distance)
            self.camera.phi = np.atan2(self.direction_unitvec[2], self.direction_unitvec[0]) + np.pi/2
            
            horizontal_unitvec = self.direction_unitvec/np.linalg.norm(self.direction_unitvec)
            horizontal_unitvec[1] = 0
            cam_pos = self.pos - self.camera_distance*horizontal_unitvec + np.array([0, 1, 0])*self.camera_height
            self.camera.x = cam_pos[0]
            self.camera.y = cam_pos[1]
            self.camera.z = cam_pos[2]


    def control(self, events):
        inputs = self.controller.get_input(events)
        if inputs["debug_mode"]:
            self.gameDebugState = GameDebugState((self.gameDebugState.value + 1) % 3)
            self.disable_inputs()
            pg.event.set_grab(False) 

        if self.gameDebugState == self.gameDebugState.FLY_DEBUG:
            pg.event.set_grab(True) 
            self.camera.control(inputs)
        else:
            self.inputs = inputs



        



    

    