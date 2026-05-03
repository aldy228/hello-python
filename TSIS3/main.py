"""
main.py — Entry point for the TSIS3 Racer game.
Controls the top-level application loop: switching between
the main menu, settings, leaderboard, and the game itself.
All screen/UI logic lives in ui.py; all game logic lives in racer.py.
"""

import pygame
from persistence import load_settings
from ui import main_menu, ask_username, leaderboard_screen, settings_screen, game_over_screen
from racer import RacerGame, WIDTH, HEIGHT


def main():
    pygame.init()  # initialize all pygame modules (display, sound, fonts, etc.)

    # Create the game window at the size defined in racer.py (400x600)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS3 Racer")

    # Clock is used in every screen to cap the frame rate at 60 FPS
    clock = pygame.time.Clock()

    # Load saved settings from settings.json (car color, difficulty, sound toggle)
    settings = load_settings()

    # ─────────────────────────────────────────────
    #  TOP-LEVEL NAVIGATION LOOP
    # Each iteration shows the main menu and handles whatever the user picks.
    # The loop only exits when the user chooses "quit" or closes the window.
    # ─────────────────────────────────────────────
    while True:
        action = main_menu(screen, clock)  # blocks until user clicks a button

        if action == "quit":
            break  # exit the main loop → pygame.quit() is called below

        elif action == "leaderboard":
            result = leaderboard_screen(screen, clock)
            if result == "quit":
                break  # user closed the window from the leaderboard screen

        elif action == "settings":
            result = settings_screen(screen, clock, settings)
            # Re-load settings after returning — the user may have changed them
            settings = load_settings()
            if result == "quit":
                break

        elif action == "play":
            # Ask for the player's name before starting the game
            username = ask_username(screen, clock)
            if username is None:
                break  # user closed the window during name entry

            # ── Inner game loop (supports Retry without going back to main menu) ──
            while True:
                # Always re-load settings so changes from the Settings screen apply
                settings = load_settings()

                # Create a fresh RacerGame instance for each run
                game = RacerGame(screen, clock, settings, username)
                status, result = game.run()  # blocks until game over or quit

                if status == "quit":
                    # Window was closed mid-game — quit immediately
                    pygame.quit()
                    return

                # Show the Game Over screen and wait for the player's choice
                next_action = game_over_screen(screen, clock, result)

                if next_action == "retry":
                    continue    # restart the inner loop → new RacerGame is created

                if next_action == "menu":
                    break       # exit inner loop → return to main menu

                if next_action == "quit":
                    pygame.quit()
                    return

    pygame.quit()  # clean up all pygame resources when the outer loop ends


# Only run main() if this script is executed directly (not imported as a module)
if __name__ == "__main__":
    main()