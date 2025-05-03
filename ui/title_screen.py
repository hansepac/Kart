import pygame
import sys
from enum import Enum

class GameState(Enum):
    TITLE = 0
    IN_GAME = 1
    CHAR_SELECT = 2
    SETTINGS = 3

def title_screen(gameState):
    pygame.init()
    WIDTH, HEIGHT = 640, 480
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Title Screen")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    buttons = [
        {"text": "Play", "state": GameState.IN_GAME},
        {"text": "Settings", "state": GameState.SETTINGS},
        {"text": "Quit", "state": GameState.TITLE},  # Exits game, but sets TITLE for demo
    ]

    button_rects = []
    base_w, base_h = 200, 60
    spacing = 20
    start_y = HEIGHT // 2 - ((base_h + spacing) * len(buttons) // 2)

    for i, btn in enumerate(buttons):
        rect = pygame.Rect(WIDTH//2 - base_w//2, start_y + i*(base_h + spacing), base_w, base_h)
        button_rects.append(rect)

    running = True
    hover_scale = 1.2
    while running:
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                gameState = GameState.TITLE
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        for i, rect in enumerate(button_rects):
            hovered = rect.collidepoint(mouse_pos)
            scale = hover_scale if hovered else 1.0
            w, h = int(base_w * scale), int(base_h * scale)
            new_rect = pygame.Rect(0, 0, w, h)
            new_rect.center = rect.center

            color = (100, 100, 255) if hovered else (80, 80, 200)
            pygame.draw.rect(screen, color, new_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), new_rect, 3, border_radius=10)

            label = font.render(buttons[i]["text"], True, (255, 255, 255))
            label_rect = label.get_rect(center=new_rect.center)
            screen.blit(label, label_rect)

            if hovered and click:
                if buttons[i]["text"] == "Quit":
                    pygame.quit()
                    sys.exit()
                else:
                    return buttons[i]["state"]

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    class GameState(Enum):
        TITLE = 0
        IN_GAME = 1
        CHAR_SELECT = 2
        SETTINGS = 3

    gameState = GameState.TITLE
    if gameState == GameState.TITLE:
        gameState = title_screen(gameState)

    print("New game state:", gameState)
