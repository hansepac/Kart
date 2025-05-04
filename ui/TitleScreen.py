import pygame as pg
import sys
from numpy import pi, sin

class TitleScreen:
    def __init__(self, screen, gameState, win_x, win_y):
        self.screen = screen
        self.bg_color = [100, 200, 255]
        self.color_phase = 0
        self.hover_scale = 1.2
        self.font = pg.font.SysFont(None, 48)
        self.buttons = [
            {"text": "Play", "state": gameState.IN_GAME},
            {"text": "Settings", "state": gameState.SETTINGS},
            {"text": "Quit", "state": gameState.TITLE},  # Exits game, but sets TITLE for demo
        ]
        self.button_rects = []
        self.base_w, self.base_h = 200, 60
        self.win_x, self.win_y = win_x, win_y
        self.spacing = 20
        self.start_y = win_y // 2 - ((self.base_h + self.spacing) * len(self.buttons) // 2)

        for i, btn in enumerate(self.buttons):
            rect = pg.Rect(self.win_x //2 - self.base_w//2, self.start_y + i*(self.base_h + self.spacing), self.base_w, self.base_h)
            self.button_rects.append(rect)

        self.mouse_pos = pg.mouse.get_pos()

    def update(self, events, dt, gameState):
        # Update the background color based on the color phase
        self.color_phase += dt * 0.25
        self.bg_color[0] = int((sin(self.color_phase) * 127) + 128)         # Red
        self.bg_color[1] = int((sin(self.color_phase + 2*pi/3) * 127) + 128)  # Green
        self.bg_color[2] = int((sin(self.color_phase + 4*pi/3) * 127) + 128)  # Blue

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
                if self.buttons[i]["text"] == "Quit":
                    pg.quit()
                    sys.exit()
                elif self.buttons[i]["state"] == gameState.IN_GAME:
                    pg.mouse.set_visible(False)
                    return self.buttons[i]["state"]
                else:
                    return self.buttons[i]["state"]
        return gameState.TITLE

    def draw(self):
        self.screen.fill(self.bg_color)
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
