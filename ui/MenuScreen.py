import pygame as pg
import sys
from numpy import pi, sin
from input import Controller

color_phase = 0

class MenuScreen:
    def __init__(self, c, buttons = [
            {"text": "Test", "value": None},
            {"text": "Example", "value": None}
        ]):
        self.button_focus = None
        self.screen = c.screen
        self.bg_color = [100, 200, 255]
        self.hover_scale = 1.2
        self.font = pg.font.SysFont(None, 48)
        self.base_w, self.base_h = 200, 60
        self.win_x, self.win_y = c.win_x, c.win_y
        self.spacing = 20
        self.start_y = c.win_y // 2 - ((self.base_h + self.spacing) * len(self.buttons) // 2)
        self.buttons = buttons
        self.button_rects_init()
        self.click = False
        self.back = False

    def button_rects_init(self):
        self.button_rects = []
        for i, btn in enumerate(self.buttons):
            rect = pg.Rect(self.win_x //2 - self.base_w//2, self.start_y + i*(self.base_h + self.spacing), self.base_w, self.base_h)
            self.button_rects.append(rect)

    def update_bg_color(self, c):
        global color_phase
        # Update the background color based on the color phase
        color_phase += c.dt * 0.25
        self.bg_color[0] = int((sin(color_phase) * 127) + 128)         # Red
        self.bg_color[1] = int((sin(color_phase + 2*pi/3) * 127) + 128)  # Green
        self.bg_color[2] = int((sin(color_phase + 4*pi/3) * 127) + 128)  # Blue

    def update_button_focus(self, c):
        # If mouse is hidden (from a menu input), turn on button focus mode
        if not pg.mouse.get_visible():
            if self.button_focus is None:
                self.button_focus = [0, 0]

        # If mouse moves
        if pg.mouse.get_rel() != (0, 0):
            self.button_focus = None
            pg.mouse.set_visible(True)

        self.click = False
        self.back = False

        for controller in c.controllers:
            if controller.ld:
                self.button_focus[0] += 1 if self.button_focus[0] < len(self.buttons) - 1 else 0
            elif controller.lu:
                self.button_focus[0] -= 1 if self.button_focus[0] > 0 else 0
            if controller.click:
                self.click = True
            if controller.back:
                self.back = True

    def update(self, c):
        # Update Background Color
        self.update_bg_color(c)
        # Udpate controller menuing bools, and connects available controllers
        for controller in c.controllers:
            controller.update_controller(c)
        # Update button focus
        self.update_button_focus(c)

        for i, rect in enumerate(self.button_rects):
            if self.button_focus is not None:
                hovered = i == self.button_focus[0]
            else:
                hovered = rect.collidepoint(pg.mouse.get_pos())

            if hovered and self.click:
                c = self.button_action(c, self.buttons[i])
        return c
    
    def button_action(self, c, button):
        if button["text"] == "Example":
            pg.quit()
            sys.exit()
        elif button["text"] == "Test":
            c.gameState = c.gameState.TITLE
            return c

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_buttons()

    def draw_buttons(self):
        for i, rect in enumerate(self.button_rects):
            if self.button_focus is not None:
                hovered = i == self.button_focus[0]
            else:
                hovered = rect.collidepoint(pg.mouse.get_pos())
            scale = self.hover_scale if hovered else 1.0
            w, h = int(self.base_w * scale), int(self.base_h * scale)
            new_rect = pg.Rect(0, 0, w, h)
            new_rect.center = rect.center

            button_color = (255,255,255) if hovered else self.bg_color
            text_color = self.bg_color if hovered else (255, 255, 255)
            pg.draw.rect(self.screen, button_color, new_rect, border_radius=10)
            pg.draw.rect(self.screen, (255, 255, 255), new_rect, 3, border_radius=10)

            label = self.font.render(self.buttons[i]["text"], True, text_color)
            label_rect = label.get_rect(center=new_rect.center)
            self.screen.blit(label, label_rect)
        


class TitleScreen(MenuScreen):
    def __init__(self, c):
        self.buttons = [
            {"text": "Start", "value": c.gameState.JOIN},
            {"text": "Controls", "value": c.gameState.CONTROLS},
            {"text": "Quit", "value": None}
        ]
        super().__init__(c, self.buttons)
        # Load original image
        original_logo = pg.image.load("assets/logo.png")
        orig_w, orig_h = original_logo.get_size()

        # Set new width (half the window width)
        new_w = self.win_x // 2.2
        new_h = int(new_w * orig_h / orig_w)
        self.start_y += new_h // 2 + self.spacing * 2 - 80

        # Scale with preserved aspect ratio
        self.logo_sprite = pg.transform.scale(original_logo, (new_w, new_h))

        # Position the logo
        self.logo_rect = self.logo_sprite.get_rect(
            center=(c.win_x // 2, round(self.start_y - new_h // 2 - self.spacing*2))
        )
        self.button_rects_init()

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_buttons()
        # Draw the image and its border
        self.screen.blit(self.logo_sprite, self.logo_rect)

    def button_action(self, c, button):
        if button["text"] == "Quit":
            pg.quit()
            sys.exit()
        else:
            c.gameState = button["value"]
        return c

class OnlineModeGameScreen(MenuScreen):
    def __init__(self, c):
        self.buttons = [
            {"text": "Host", "value": [c.gameState.IN_GAME, c.onlineState.HOST]},
            {"text": "Join", "value": [c.gameState.IN_GAME, c.onlineState.CLIENT]},
            {"text": "Local", "value": [c.gameState.IN_GAME, c.onlineState.LOCAL]},
            {"text": "Back", "value": [c.gameState.TITLE, c.onlineState.LOCAL]}
        ]
        super().__init__(c, self.buttons)

    def button_action(self, c, button):
        c.gameState, c.onlineState = button["value"]
        return c
        
class FindGameMenuScreen(MenuScreen):
    def __init__(self, c):
        self.buttons = [
            {"text": "Find Game", "value": [c.gameState.IN_GAME, c.onlineState.CLIENT]},
            {"text": "Back", "value": [c.gameState.TITLE, c.onlineState.LOCAL]}
        ]
        super().__init__(c, self.buttons)

    # def button_action(self, c, button):
    #     if button["value"][0] == states[0].IN_GAME:
    #         pg.mouse.set_visible(False)
    #         return button["value"][0], button["value"][1]
    #     else:
    #         pg.mouse.set_visible(True)
    #         return button["value"][0], button["value"][1]
        
# class ChangeControlsScreen(MenuScreen):
#     def __init__(self, c):
#         self.buttons = [
#             {"text": "Find Game", "value": [c.gameState.IN_GAME, c.onlineState.CLIENT]},
#             {"text": "Back", "value": [c.gameState.TITLE, c.onlineState.LOCAL]}
#         ]
#         super().__init__(c, self.buttons)

#     def button_action(self, c, button):
#         if button["value"][0] == states[0].IN_GAME:
#             pg.mouse.set_visible(False)
#             return button["value"][0], button["value"][1]
#         else:
#             pg.mouse.set_visible(True)
#             return button["value"][0], button["value"][1]
        
class ControllerScreen(MenuScreen):
    def __init__(self, c):
        self.screen = c.screen
        self.focused = [0,0]
        self.hover_scale = 1.2
        self.bg_color = [100, 200, 255]
        self.font = pg.font.SysFont(None, 48)
        self.base_w, self.base_h = 200, 60
        self.spacing_x, self.spacing_y = 20, 10
        self.mouse_pos = pg.mouse.get_pos()
        self.controls = {
            "Gas": "gas",
            "Reverse": "reverse",
            "Brake": "brake",
            "Right": "right",
            "Left": "left",
            "Drift": "drift",
            "Use Item": "use_item"
        }
        self.buttons = [[{"text": "Input Type", "is_button": False}]]
        self.contol_attrs = [value for value in self.controls.values()]
        if c.DEV_MODE:
            self.controls["Debug"] = "enable_debug_mode"
        super().__init__(c, self.buttons)
        self.update_buttons(c)
    
    def button_action(self, c, i, j):
        button = self.buttons[j][i]
        if button["text"] == "Add":
            c.controllers.append(Controller(is_controller=True))
        elif button["text"] == "Back":
            c.gameState = c.gameState.TITLE
        elif j >= 1 and j <= len(self.buttons) + 1:
            if button["text"] == "Remove":
                c.controllers.pop(j - 1)
            elif button["text"] == "Keyboard" or button["text"] == "Controller":
                c.controllers[j - 1].switch_input_mode(c)
            else:
                while True:
                    for event in pg.event.get():
                        if event.type == pg.KEYDOWN:
                            setattr(c.controllers[j - 1], self.contol_attrs[i-1], event.key)
                            return c
                        elif event.type == pg.JOYBUTTONDOWN:
                            setattr(c.controllers[j - 1], self.contol_attrs[i-1], event.button)
                            return c
        else:
            IndexError(f"Button index out of range: {j} {i}")

        self.update_buttons(c)
        return c

    def update_buttons(self, c):
        # Far Left Column of Text
        self.buttons = [[{"text": "Input Type", "is_button": False}]]
        self.buttons[0] += [{"text": key, "is_button": False} for key in self.controls]

        controller_buttons = ["A", "B", "Y", "X", "LB", "RB", "MENU"]

        def get_input_value(controller, value):
            if controller.joystick is not None:
                if getattr(controller, value) >= len(controller_buttons):
                    return "UNKN"
                return controller_buttons[getattr(controller, value)]
            else:
                return pg.key.name(getattr(controller, value))

        for i, controller in enumerate(c.controllers):
            input_type = "Controller" if controller.is_controller else "Keyboard"
            self.buttons.append(
                [
                    {"text": input_type, "is_button": True},
                    *[{"text": f"{get_input_value(controller, value)}", "is_button": True} for value in self.controls.values()],
                    {"text": "Remove", "is_button": True},
                ]
            )
        if len(c.controllers) < 4:
            self.buttons.append([{"text": "Add", "is_button": True}, {"text": "Back", "is_button": True}])
        else:
            self.buttons.append([{"text": "Back", "is_button": True}])
        self.button_rects = []

        rows = max(len(row) for row in self.buttons)
        cols = len(self.buttons)

        total_width = cols * self.base_w + (cols - 1) * self.spacing_x
        total_height = rows * self.base_h + (rows - 1) * self.spacing_y

        start_x = (c.win_x - total_width) // 2
        start_y = (c.win_y - total_height) // 2

        for col_idx, col in enumerate(self.buttons):
            col_rects = []
            for row_idx, _ in enumerate(col):
                x = start_x + col_idx * (self.base_w + self.spacing_x)
                y = start_y + row_idx * (self.base_h + self.spacing_y)
                rect = pg.Rect(x, y, self.base_w, self.base_h)
                col_rects.append(rect)
            self.button_rects.append(col_rects)

    def update(self, c):
        self.update_bg_color(c)
        # Udpate controller menuing bools, and connects available controllers
        for controller in c.controllers:
            controller.update_controller(c)

        self.update_buttons(c)

        self.update_button_focus(c)

        for j, col in enumerate(self.button_rects):
            for i, rect in enumerate(col):
                if self.button_focus is not None:
                    hovered = i == self.button_focus[0]
                else:
                    hovered = rect.collidepoint(pg.mouse.get_pos())
                if hovered and self.click and self.buttons[j][i]["is_button"]:
                    c = self.button_action(c, i, j)
        return c

    def draw(self, invert=False):
        self.screen.fill(self.bg_color)
        self.draw_buttons(invert)

    def draw_buttons(self, invert=False):
        for j, col in enumerate(self.button_rects):
            for i, rect in enumerate(col):
                self.draw_button(i, j, invert)
                
    def draw_button(self, i, j, invert=False, color = None):
        text_color = (255, 255, 255)
        if self.buttons[j][i]["is_button"]:
            if self.button_focus is not None:
                hovered = i == self.button_focus[0]
            else:
                hovered = self.button_rects[j][i].collidepoint(pg.mouse.get_pos())
            scale = self.hover_scale if hovered else 1.0

            if not invert or color:
                if color:
                    button_color = color
                else:
                    button_color = (255, 255, 255) if hovered else self.bg_color
                w, h = int(self.base_w * scale), int(self.base_h * scale)
                new_rect = pg.Rect(0, 0, w, h)
                new_rect.center = self.button_rects[j][i].center
                pg.draw.rect(self.screen, button_color, new_rect, border_radius=10)

            text_color = self.bg_color if hovered else (255, 255, 255)
            pg.draw.rect(self.screen, (255, 255, 255), new_rect, 3, border_radius=10)

        button_text = self.buttons[j][i]["text"]
        label = self.font.render(button_text, True, text_color)
        label_rect = label.get_rect(center=self.button_rects[j][i].center)
        self.screen.blit(label, label_rect)

class MenuCore:
    def __init__(self, c):
        self.titleScreen = TitleScreen(c)
        self.onlineModeGameScreen = OnlineModeGameScreen(c)
        self.controllerScreen = ControllerScreen(c)