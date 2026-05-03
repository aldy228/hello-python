import pygame
from persistence import load_leaderboard, save_settings

WIDTH = 400
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DARK_GRAY = (70, 70, 70)
BLUE = (40, 120, 255)
GREEN = (70, 190, 90)
RED = (220, 70, 70)
YELLOW = (240, 210, 60)


def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("Verdana", size)
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)
    return rect


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = GRAY if self.rect.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        draw_text(surface, self.text, 22, BLACK, self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def ask_username(screen, clock):
    """Simple username entry before starting."""
    name = ""
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode

        screen.fill((35, 35, 35))
        draw_text(screen, "Enter your name", 32, WHITE, WIDTH // 2, 170)

        input_rect = pygame.Rect(70, 250, 260, 50)
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=8)
        pygame.draw.rect(screen, BLUE, input_rect, 3, border_radius=8)
        draw_text(screen, name if name else "Player", 25, BLACK, WIDTH // 2, 275)

        draw_text(screen, "Press ENTER to start", 18, WHITE, WIDTH // 2, 350)
        pygame.display.update()
        clock.tick(60)

    return name.strip() if name.strip() else "Player"


def main_menu(screen, clock):
    buttons = {
        "play": Button("Play", 110, 210, 180, 50),
        "leaderboard": Button("Leaderboard", 110, 280, 180, 50),
        "settings": Button("Settings", 110, 350, 180, 50),
        "quit": Button("Quit", 110, 420, 180, 50)
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            for action, button in buttons.items():
                if button.clicked(event):
                    return action

        screen.fill((30, 90, 60))
        draw_text(screen, "RACER TSIS3", 38, WHITE, WIDTH // 2, 100)
        draw_text(screen, "Use LEFT and RIGHT only", 17, WHITE, WIDTH // 2, 145)

        for button in buttons.values():
            button.draw(screen)

        pygame.display.update()
        clock.tick(60)


def leaderboard_screen(screen, clock):
    back = Button("Back", 125, 520, 150, 45)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back.clicked(event):
                return "menu"

        scores = load_leaderboard()
        screen.fill((35, 35, 60))
        draw_text(screen, "Top 10 Scores", 32, WHITE, WIDTH // 2, 50)
        draw_text(screen, "Rank   Name        Score   Dist", 16, YELLOW, 40, 100, center=False)

        y = 135
        if not scores:
            draw_text(screen, "No scores yet", 20, WHITE, WIDTH // 2, 250)
        else:
            for i, item in enumerate(scores, start=1):
                line = f"{i:<2}     {item['name'][:9]:<9}  {item['score']:<5}   {item['distance']}m"
                draw_text(screen, line, 15, WHITE, 40, y, center=False)
                y += 35

        back.draw(screen)
        pygame.display.update()
        clock.tick(60)


def settings_screen(screen, clock, settings):
    sound_button = Button("", 70, 170, 260, 45)
    color_button = Button("", 70, 240, 260, 45)
    difficulty_button = Button("", 70, 310, 260, 45)
    back = Button("Back", 125, 500, 150, 45)

    colors = ["Orange", "Blue", "Yellow", "Green", "Purple"]
    difficulties = ["Easy", "Normal", "Hard"]

    while True:
        sound_button.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
        color_button.text = f"Car color: {settings['car_color']}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return "quit"

            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            if color_button.clicked(event):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)

            if difficulty_button.clicked(event):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)

            if back.clicked(event):
                save_settings(settings)
                return "menu"

        screen.fill((45, 45, 45))
        draw_text(screen, "Settings", 36, WHITE, WIDTH // 2, 85)
        draw_text(screen, "Click buttons to change options", 16, WHITE, WIDTH // 2, 125)

        sound_button.draw(screen)
        color_button.draw(screen)
        difficulty_button.draw(screen)
        back.draw(screen)

        pygame.display.update()
        clock.tick(60)


def game_over_screen(screen, clock, result):
    retry = Button("Retry", 70, 430, 120, 50)
    menu = Button("Main Menu", 210, 430, 120, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"

        screen.fill((110, 30, 30))
        draw_text(screen, "Game Over", 42, WHITE, WIDTH // 2, 100)
        draw_text(screen, f"Score: {result['score']}", 23, WHITE, WIDTH // 2, 185)
        draw_text(screen, f"Distance: {result['distance']} m", 23, WHITE, WIDTH // 2, 225)
        draw_text(screen, f"Coins: {result['coins']}", 23, WHITE, WIDTH // 2, 265)
        draw_text(screen, f"Player: {result['name']}", 20, YELLOW, WIDTH // 2, 320)

        retry.draw(screen)
        menu.draw(screen)
        pygame.display.update()
        clock.tick(60)