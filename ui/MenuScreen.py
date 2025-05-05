import pygame as pg
import sys
from numpy import pi, sin
from input import Controller

color_phase = 0

class MenuScreen:
    def __init__(self, screen, win_x, win_y, buttons = [
            {"text": "Test", "value": None},
            {"text": "Example", "value": None}
        ]):
        self.button_focus = None
        self.screen = screen
        self.bg_color = [100, 200, 255]
        self.hover_scale = 1.2
        self.font = pg.font.SysFont(None, 48)
        self.base_w, self.base_h = 200, 60
        self.win_x, self.win_y = win_x, win_y
        self.spacing = 20
        self.start_y = win_y // 2 - ((self.base_h + self.spacing) * len(self.buttons) // 2)
        self.buttons = buttons
        self.button_rects_init()

    def button_rects_init(self):
        self.button_rects = []
        for i, btn in enumerate(self.buttons):
            rect = pg.Rect(self.win_x //2 - self.base_w//2, self.start_y + i*(self.base_h + self.spacing), self.base_w, self.base_h)
            self.button_rects.append(rect)
        
        self.mouse_pos = pg.mouse.get_pos()

    def update(self, events, dt):
        global color_phase
        # Update the background color based on the color phase
        color_phase += dt * 0.25
        self.bg_color[0] = int((sin(color_phase) * 127) + 128)         # Red
        self.bg_color[1] = int((sin(color_phase + 2*pi/3) * 127) + 128)  # Green
        self.bg_color[2] = int((sin(color_phase + 4*pi/3) * 127) + 128)  # Blue

        # Get Button Clicks
        self.mouse_pos = pg.mouse.get_pos()
        click = False
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        for i, rect in enumerate(self.button_rects):
            hovered = rect.collidepoint(self.mouse_pos)

            if hovered and click:
                return self.button_action(self.buttons[i])
        return None
    
    def button_action(self, button, state):
        if button["text"] == "Example":
            pg.quit()
            sys.exit()
        elif button["text"] == "Test":
            return button

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_buttons()

    def draw_buttons(self):
        for i, rect in enumerate(self.button_rects):
                hovered = rect.collidepoint(self.mouse_pos)
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
    def __init__(self, screen, gameState, win_x, win_y):
        self.buttons = [
            {"text": "Start", "value": gameState.JOIN},
            {"text": "Controls", "value": gameState.CONTROLS},
            {"text": "Quit", "value": None}
        ]
        super().__init__(screen, win_x, win_y, self.buttons)
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
            center=(win_x // 2, round(self.start_y - new_h // 2 - self.spacing*2))
        )
        self.button_rects_init()

    def draw(self):
        self.screen.fill(self.bg_color)
        self.draw_buttons()
        # Draw the image and its border
        self.screen.blit(self.logo_sprite, self.logo_rect)

    def button_action(self, button):
        if button["text"] == "Quit":
            pg.quit()
            sys.exit()
        else:
            return button

class OnlineModeGameScreen(MenuScreen):
    def __init__(self, screen, gameState, onlineState, win_x, win_y):
        self.buttons = [
            {"text": "Host", "value": [gameState.IN_GAME, onlineState.HOST]},
            {"text": "Join", "value": [gameState.IN_GAME, onlineState.CLIENT]},
            {"text": "Local", "value": [gameState.IN_GAME, onlineState.LOCAL]},
            {"text": "Back", "value": [gameState.TITLE, onlineState.LOCAL]}
        ]
        super().__init__(screen, win_x, win_y, self.buttons)

    def button_action(self, button):
        if button["value"] == "Host":
            pg.mouse.set_visible(False)
        else:
            pg.mouse.set_visible(True)
        return button
        
class FindGameMenuScreen(MenuScreen):
    def __init__(self, screen, gameState, onlineState, win_x, win_y):
        self.buttons = [
            {"text": "Find Game", "value": [gameState.IN_GAME, onlineState.CLIENT]},
            {"text": "Back", "value": [gameState.TITLE, onlineState.LOCAL]}
        ]
        super().__init__(screen, win_x, win_y, self.buttons)

    def button_action(self, button, states):
        if button["value"][0] == states[0].IN_GAME:
            pg.mouse.set_visible(False)
            return button["value"][0], button["value"][1]
        else:
            pg.mouse.set_visible(True)
            return button["value"][0], button["value"][1]
        
class ChangeControlsScreen(MenuScreen):
    def __init__(self, screen, gameState, onlineState, win_x, win_y):
        self.buttons = [
            {"text": "Find Game", "value": [gameState.IN_GAME, onlineState.CLIENT]},
            {"text": "Back", "value": [gameState.TITLE, onlineState.LOCAL]}
        ]
        super().__init__(screen, win_x, win_y, self.buttons)

    def button_action(self, button, states):
        if button["value"][0] == states[0].IN_GAME:
            pg.mouse.set_visible(False)
            return button["value"][0], button["value"][1]
        else:
            pg.mouse.set_visible(True)
            return button["value"][0], button["value"][1]
        
class ControllerScreen:
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
        self.contol_attrs = [value for value in self.controls.values()]
        if c.DEV_MODE:
            self.controls["Debug"] = "enable_debug_mode"
        self.update_buttons(c)
    
    def button_action(self, c, i, j):
        button = self.buttons[j][i]
        print(f"Button: {button}")
        if button["text"] == "Add":
            c.controllers.append(Controller(is_controller=True))
        elif button["text"] == "Back":
            c.gameState = c.gameState.TITLE
        elif j >= 1 and j <= len(self.buttons) + 1:
            if button["text"] == "Remove":
                c.controllers.pop(j - 1)
            elif button["text"] == "Keyboard" or button["text"] == "Controller":
                c.controllers[j - 1].is_controller = not c.controllers[j - 1].is_controller
            else:
                while True:
                    for event in pg.event.get():
                        if event.type == pg.KEYDOWN:
                            print(pg.key.name(getattr(c.controllers[j-1], self.contol_attrs[i-1])))
                            setattr(c.controllers[j - 1], self.contol_attrs[i-1], event.key)
                            print(pg.key.name(getattr(c.controllers[j-1], self.contol_attrs[i-1])))
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
        self.buttons = [[{"text": "Input Type"}]]
        self.buttons[0] += [{"text": key} for key in self.controls]

        for i, controller in enumerate(c.controllers):
            input_type = "Controller" if controller.is_controller else "Keyboard"
            self.buttons.append(
                [
                    {"text": input_type},
                    *[{"text": f"{pg.key.name(getattr(controller, value))}"} for value in self.controls.values()],
                    {"text": "Remove"},
                ]
            )
        self.buttons.append([{"text": "Add"}, {"text": "Back"}])
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
        global color_phase
        # Update the background color based on the color phase
        color_phase += c.dt * 0.25
        self.bg_color[0] = int((sin(color_phase) * 127) + 128)         # Red
        self.bg_color[1] = int((sin(color_phase + 2*pi/3) * 127) + 128)  # Green
        self.bg_color[2] = int((sin(color_phase + 4*pi/3) * 127) + 128)  # Blue

        # Get Button Clicks
        self.mouse_pos = pg.mouse.get_pos()
        click = False
        for event in c.events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        for j, col in enumerate(self.button_rects):
            for i, rect in enumerate(col):
                if rect.collidepoint(self.mouse_pos) and click:
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
        hovered = self.button_rects[j][i].collidepoint(self.mouse_pos)
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
        label_rect = label.get_rect(center=new_rect.center)
        self.screen.blit(label, label_rect)

class MenuCore:
    def __init__(self, c):
        self.titleScreen = TitleScreen(c.screen, c.gameState, c.win_x, c.win_y)
        self.onlineModeGameScreen = OnlineModeGameScreen(c.screen, c.gameState, c.onlineState, c.win_x, c.win_y)
        self.controllerScreen = ControllerScreen(c)