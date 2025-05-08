import numpy as np
from .Driver import Driver
from entities.Camera import Camera
from input import Controller
from utils.states import GameDebugState
from ui import draw_debug_text, draw_speedometer, show_keyboard_ui, draw_minimap, draw_boost_bar
from entities.Renderable import *

class LocalPlayer(Driver):
    # it already has position and velocity stuff
    def __init__(self, mapmaster, player_screen, pos = np.array([0.0, 0.0, 0.0]), direction_unitvec = np.array([1.0, 0.0, 0.0]), controller: Controller = Controller(), car_sprite = 0):
        super().__init__(mapmaster, pos = pos, direction_unitvec = direction_unitvec, car_sprite=car_sprite)
        self.controller: Controller = controller
        self.camera = Camera(*pos, np.atan2(direction_unitvec[2], direction_unitvec[0]), nx = player_screen.get_size()[0], ny = player_screen.get_size()[1])
        self.camera_height = 0.2
        self.camera_distance = 0.3
        self.camera_theta = 0.2
        self.gameDebugState: GameDebugState = GameDebugState(0)

        self.screen = player_screen
        self.name = "Local Player"

    def render_player_view(self, clock):

        angle = (self.camera.theta + np.pi/2)/np.pi
        sky_color = (0, round(angle*200), round(angle*255))
        self.screen.fill(sky_color)

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

        # add trees 
        trees, biome_indices = self.terrainDynamic.get_trees()
        for i in range(len(trees)):
            nontriangle_renderables.append(TreeSprite(trees[i], biome_indices[i]))

        # sort renderables according to depth
        all_renderables = calculateRenderableScreenCoords(self.camera, nontriangle_renderables, triangle_renderables)
        all_renderables.sort(key=lambda r: r.screen_depth, reverse=True)

        # now draw renderables
        for renderable in all_renderables:
            if renderable is not player_renderable:
                renderable.draw(self.screen)
        player_renderable.draw(self.screen, is_player=True) # draw this player last

        window_x, window_y = self.screen.get_size()
        radius = 100
        draw_speedometer(self.screen, self.actual_speed*1250, (radius+70, radius+70), radius=radius, max_val=100, tick_step=10)
        
        if not self.controller.is_controller:

            show_keyboard_ui(self.screen, (window_x-350, window_y-350))
        
        
        # UI stuff
        draw_minimap(self.screen, self.pos, self.direction_unitvec, nontriangle_renderables, (30,2*radius+60), radius=100)
        draw_boost_bar(self.screen, self.drift_multiplier, self.drift_multiplier_max, self.drift_boost_threshold, x=20, y = 80)

        # Stylish racing HUD text
        font = pg.font.Font("assets/fonts/SpeedRush.ttf", 40) if pg.font.get_init() else pg.font.Font(None, 40)
        text = f"Rank: {self.rank}  Flag: {self.flag_index if not self.completed else self.mapmaster.num_flags}/{self.mapmaster.num_flags}"
        pulse = int(128 + 127 * math.sin(pg.time.get_ticks() * 0.003))
        color = (255, pulse, 0)
        shadow = font.render(text, True, (0, 0, 0))
        main = font.render(text, True, color)
        box = pg.Surface(main.get_size(), pg.SRCALPHA); box.fill((0, 0, 0, 150))
        self.screen.blit(box, (10, 10))
        self.screen.blit(shadow, (12, 12))
        self.screen.blit(main, (10, 10))

        
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


    def control(self):
        inputs = self.controller.get_input()
        if inputs["debug_mode"]:
            self.gameDebugState = GameDebugState((self.gameDebugState.value + 1) % 3)
            self.disable_inputs()
            pg.event.set_grab(False) 

        if self.gameDebugState == self.gameDebugState.FLY_DEBUG:
            pg.event.set_grab(True) 
            self.camera.control(inputs, pg.mouse.get_rel())
        else:
            self.inputs = inputs



        



    

    