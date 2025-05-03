import pygame as pg

font = pg.font.SysFont(None, 24)

def show_keyboard_ui(screen, center):
    # Define keys and positions
    keys = {
        "W": {"key": pg.K_w, "pos": (170, 60)},
        "A": {"key": pg.K_a, "pos": (120, 110)},
        "S": {"key": pg.K_s, "pos": (170, 110)},
        "D": {"key": pg.K_d, "pos": (220, 110)},
        "SHIFT": {"key": pg.K_LSHIFT, "pos": (50, 200)},
        "CTRL": {"key": pg.K_LCTRL, "pos": (50, 250)},
        "SPACE": {"key": pg.K_SPACE, "pos": (120, 200), "size": (160, 40)},
    }

    pressed = pg.key.get_pressed()

    for label, info in keys.items():
        key = info["key"]
        x, y = info["pos"]
        w, h = info.get("size", (50, 40))
        is_pressed = pressed[key]
        color = (0, 200, 0) if is_pressed else (80, 80, 80)
        x += center[0]
        y += center[1]

        pg.draw.rect(screen, color, (x, y, w, h), border_radius=6)
        pg.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2, border_radius=6)

        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text, text_rect)