import pygame
import sys

def character_selection_ui(character_dict):
    pygame.init()
    WIDTH, HEIGHT = 400, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    rect_width = 300
    rect_height = 500
    rect_x = (WIDTH - rect_width) // 2
    rect_y = (HEIGHT - rect_height) // 2

    index = 0
    is_animating = False
    animation_offset = 0
    animation_dir = 0  # 1 = up, -1 = down
    animation_speed = 20

    def draw_ui(offset=0):
        # Background color from current index
        bg_color = character_dict["color"][index]
        pygame.draw.rect(screen, bg_color, (rect_x, rect_y, rect_width, rect_height))

        # Border
        pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 4)

        # Sprite drawing
        sprite = character_dict["sprites"][index]
        sprite_rect = sprite.get_rect(center=(WIDTH // 2, HEIGHT // 2 + offset))
        screen.blit(sprite, sprite_rect)

        # Character name
        name = character_dict["character_name"][index]
        label = font.render(name, True, (0, 0, 0))
        label_rect = label.get_rect(center=(WIDTH // 2, rect_y + rect_height - 40))
        screen.blit(label, label_rect)

    running = True
    while running:
        screen.fill((20, 20, 20))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not is_animating and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and index > 0:
                    animation_dir = 1
                    is_animating = True
                    next_index = index - 1
                elif event.key == pygame.K_DOWN and index < len(character_dict["sprites"]) - 1:
                    animation_dir = -1
                    is_animating = True
                    next_index = index + 1

        if is_animating:
            animation_offset += animation_speed * animation_dir
            draw_ui(offset=animation_offset)
            # Draw the incoming sprite
            sprite = character_dict["sprites"][next_index]
            incoming_y = HEIGHT // 2 - animation_dir * rect_height + animation_offset
            incoming_rect = sprite.get_rect(center=(WIDTH // 2, incoming_y))
            incoming_bg = character_dict["color"][next_index]
            pygame.draw.rect(screen, incoming_bg, (rect_x, rect_y, rect_width, rect_height))
            pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 4)
            screen.blit(sprite, incoming_rect)
            label = font.render(character_dict["character_name"][next_index], True, (0, 0, 0))
            label_rect = label.get_rect(center=(WIDTH // 2, rect_y + rect_height - 40))
            screen.blit(label, label_rect)

            if abs(animation_offset) >= rect_height:
                index = next_index
                animation_offset = 0
                is_animating = False
        else:
            draw_ui()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    def make_dummy_sprite(color):
        surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (50, 50), 50)
        return surf

    character_data = {
        "sprites": [make_dummy_sprite((255, 0, 0)), make_dummy_sprite((0, 255, 0)), make_dummy_sprite((0, 0, 255))],
        "character_name": ["Red", "Green", "Blue"],
        "color": [(255, 200, 200), (200, 255, 200), (200, 200, 255)]
    }

    character_selection_ui(character_data)
