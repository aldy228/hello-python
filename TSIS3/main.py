import pygame
from persistence import load_settings
from ui import main_menu, ask_username, leaderboard_screen, settings_screen, game_over_screen
from racer import RacerGame, WIDTH, HEIGHT


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS3 Racer")
    clock = pygame.time.Clock()

    settings = load_settings()

    while True:
        action = main_menu(screen, clock)

        if action == "quit":
            break

        elif action == "leaderboard":
            result = leaderboard_screen(screen, clock)
            if result == "quit":
                break

        elif action == "settings":
            result = settings_screen(screen, clock, settings)
            settings = load_settings()  # apply saved settings immediately
            if result == "quit":
                break

        elif action == "play":
            username = ask_username(screen, clock)
            if username is None:
                break

            while True:
                settings = load_settings()
                game = RacerGame(screen, clock, settings, username)
                status, result = game.run()

                if status == "quit":
                    pygame.quit()
                    return

                next_action = game_over_screen(screen, clock, result)
                if next_action == "retry":
                    continue
                if next_action == "menu":
                    break
                if next_action == "quit":
                    pygame.quit()
                    return

    pygame.quit()


if __name__ == "__main__":
    main()