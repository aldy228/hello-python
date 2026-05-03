"""
ui.py — All screen/menu logic for the TSIS3 Racer game.
Contains standalone functions for each screen (main menu, leaderboard,
settings, game over) plus the Button class and helper utilities.
None of these functions know about the game internals — they only
return string action codes like "play", "menu", "quit" back to main.py.
"""

import pygame
from persistence import load_leaderboard, save_settings

WIDTH  = 400
HEIGHT = 600

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
WHITE     = (255, 255, 255)
BLACK     = (20,  20,  20)
GRAY      = (180, 180, 180)
DARK_GRAY = (70,  70,  70)
BLUE      = (40,  120, 255)
GREEN     = (70,  190, 90)
RED       = (220, 70,  70)
YELLOW    = (240, 210, 60)


# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────

def draw_text(surface, text, size, color, x, y, center=True):
    """
    Render a text string onto a surface at position (x, y).

    Parameters:
        surface (pygame.Surface): where to draw
        text    (str): the string to display
        size    (int): font size in points
        color   (tuple): RGB color
        x, y    (int): position on the surface
        center  (bool): if True, (x,y) is the center of the text;
                        if False, (x,y) is the top-left corner

    Returns:
        rect (pygame.Rect): the bounding rectangle of the rendered text
                            (useful for positioning follow-up elements)
    """
    font  = pygame.font.SysFont("Verdana", size)
    image = font.render(text, True, color)
    rect  = image.get_rect()

    if center:
        rect.center   = (x, y)
    else:
        rect.topleft  = (x, y)

    surface.blit(image, rect)
    return rect


# ─────────────────────────────────────────────
#  BUTTON CLASS
# ─────────────────────────────────────────────

class Button:
    """
    A clickable rectangular button with a text label.

    Highlights (turns gray) when the mouse hovers over it.
    Use clicked(event) to detect a left-click on this button.
    """

    def __init__(self, text, x, y, w, h):
        """
        Parameters:
            text    (str): label displayed on the button
            x, y    (int): top-left position of the button
            w, h    (int): width and height of the button
        """
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        """
        Draw the button on the given surface.
        The button turns gray when the mouse is hovering over it (hover effect).
        The label is always centered inside the button.
        self.text is read each frame, so changing it between frames updates the label
        (used in settings_screen to show current values like "Sound: On").
        """
        mouse_pos = pygame.mouse.get_pos()
        # Hover: gray background when mouse is over the button, white otherwise
        color = GRAY if self.rect.collidepoint(mouse_pos) else WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=10)  # filled background
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # border outline
        draw_text(surface, self.text, 22, BLACK, self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        """
        Return True if this button was left-clicked in the given event.
        Only responds to MOUSEBUTTONDOWN events (button=1 means left click).
        collidepoint checks whether the click landed inside the button's rectangle.
        """
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ─────────────────────────────────────────────
#  USERNAME ENTRY SCREEN
# ─────────────────────────────────────────────

def ask_username(screen, clock):
    """
    Show a simple text-input screen where the player enters their name.
    The name is limited to 12 printable characters.
    Pressing Enter confirms; closing the window returns None (signals quit).

    Returns:
        str: the entered name, or "Player" if the field was left blank
        None: if the window was closed
    """
    name   = ""   # accumulates the typed characters
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # window closed — signal main.py to exit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False  # confirm and exit the loop

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]  # remove the last character

                elif len(name) < 12 and event.unicode.isprintable():
                    # isprintable() filters out control characters (arrows, F-keys, etc.)
                    name += event.unicode

        # ── Draw the screen ──
        screen.fill((35, 35, 35))
        draw_text(screen, "Enter your name", 32, WHITE, WIDTH // 2, 170)

        # Input box — always visible, shows placeholder "Player" if empty
        input_rect = pygame.Rect(70, 250, 260, 50)
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=8)
        pygame.draw.rect(screen, BLUE,  input_rect, 3, border_radius=8)
        draw_text(screen, name if name else "Player", 25, BLACK, WIDTH // 2, 275)

        draw_text(screen, "Press ENTER to start", 18, WHITE, WIDTH // 2, 350)
        pygame.display.update()
        clock.tick(60)

    # Strip whitespace; fall back to "Player" if the result is empty
    return name.strip() if name.strip() else "Player"


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def main_menu(screen, clock):
    """
    Display the main menu with four buttons.
    Blocks until the user clicks a button or closes the window.

    Returns:
        str: one of "play", "leaderboard", "settings", "quit"
    """
    # Each button maps to an action string returned to main.py
    buttons = {
        "play":        Button("Play",        110, 210, 180, 50),
        "leaderboard": Button("Leaderboard", 110, 280, 180, 50),
        "settings":    Button("Settings",    110, 350, 180, 50),
        "quit":        Button("Quit",        110, 420, 180, 50)
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # Check all buttons — return the action string for whichever was clicked
            for action, button in buttons.items():
                if button.clicked(event):
                    return action

        # ── Draw the menu ──
        screen.fill((30, 90, 60))  # dark green background
        draw_text(screen, "RACER TSIS3",           38, WHITE, WIDTH // 2, 100)
        draw_text(screen, "Use LEFT and RIGHT only", 17, WHITE, WIDTH // 2, 145)

        for button in buttons.values():
            button.draw(screen)

        pygame.display.update()
        clock.tick(60)


# ─────────────────────────────────────────────
#  LEADERBOARD SCREEN
# ─────────────────────────────────────────────

def leaderboard_screen(screen, clock):
    """
    Display the top 10 scores loaded from leaderboard.json.
    Scores are re-loaded every frame so new entries appear immediately.
    Pressing Back returns to the main menu.

    Returns:
        str: "menu" or "quit"
    """
    back = Button("Back", 125, 520, 150, 45)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if back.clicked(event):
                return "menu"

        # Re-load scores every frame (cheap, and ensures fresh data after a game)
        scores = load_leaderboard()

        screen.fill((35, 35, 60))  # dark blue background
        draw_text(screen, "Top 10 Scores", 32, WHITE,  WIDTH // 2, 50)
        draw_text(screen, "Rank   Name        Score   Dist", 16, YELLOW, 40, 100, center=False)

        y = 135
        if not scores:
            draw_text(screen, "No scores yet", 20, WHITE, WIDTH // 2, 250)
        else:
            for i, item in enumerate(scores, start=1):
                # Left-aligned fixed-width columns using Python f-string formatting
                # :<2 = left-align in 2 chars, :<9 = left-align in 9 chars, etc.
                line = f"{i:<2}     {item['name'][:9]:<9}  {item['score']:<5}   {item['distance']}m"
                draw_text(screen, line, 15, WHITE, 40, y, center=False)
                y += 35  # move down for the next row

        back.draw(screen)
        pygame.display.update()
        clock.tick(60)


# ─────────────────────────────────────────────
#  SETTINGS SCREEN
# ─────────────────────────────────────────────

def settings_screen(screen, clock, settings):
    """
    Display toggleable settings: Sound, Car Color, Difficulty.
    Each button cycles through its available options on click.
    Settings are saved to settings.json after every change.

    The button labels are updated each frame to reflect the current values
    (e.g. "Sound: On" / "Sound: Off") — this works because Button.text
    is just a string that draw() reads fresh every frame.

    Parameters:
        settings (dict): the current settings dict (modified in place)

    Returns:
        str: "menu" or "quit"
    """
    sound_button      = Button("", 70, 170, 260, 45)
    color_button      = Button("", 70, 240, 260, 45)
    difficulty_button = Button("", 70, 310, 260, 45)
    back              = Button("Back", 125, 500, 150, 45)

    # Available options for cycled settings — clicking steps to the next item
    colors       = ["Orange", "Blue", "Yellow", "Green", "Purple"]
    difficulties = ["Easy", "Normal", "Hard"]

    while True:
        # Update button labels to show the current value (done every frame)
        sound_button.text      = f"Sound: {'On' if settings['sound'] else 'Off'}"
        color_button.text      = f"Car color: {settings['car_color']}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return "quit"

            if sound_button.clicked(event):
                # Toggle: True → False → True ...
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            if color_button.clicked(event):
                # Cycle to the next color in the list (wraps around with %)
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]
                save_settings(settings)

            if difficulty_button.clicked(event):
                # Cycle to the next difficulty level
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]
                save_settings(settings)

            if back.clicked(event):
                save_settings(settings)
                return "menu"

        # ── Draw the settings screen ──
        screen.fill((45, 45, 45))
        draw_text(screen, "Settings",                    36, WHITE, WIDTH // 2, 85)
        draw_text(screen, "Click buttons to change options", 16, WHITE, WIDTH // 2, 125)

        sound_button.draw(screen)
        color_button.draw(screen)
        difficulty_button.draw(screen)
        back.draw(screen)

        pygame.display.update()
        clock.tick(60)


# ─────────────────────────────────────────────
#  GAME OVER SCREEN
# ─────────────────────────────────────────────

def game_over_screen(screen, clock, result):
    """
    Display the end-of-game summary: score, distance, coins, player name.
    The player can choose to retry (new game, same username) or return to menu.

    Parameters:
        result (dict): contains "score", "distance", "coins", "name"

    Returns:
        str: "retry", "menu", or "quit"
    """
    retry = Button("Retry",     70,  430, 120, 50)
    menu  = Button("Main Menu", 210, 430, 120, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"

        # ── Draw the game over screen ──
        screen.fill((110, 30, 30))  # dark red background
        draw_text(screen, "Game Over",                   42, WHITE,  WIDTH // 2, 100)
        draw_text(screen, f"Score: {result['score']}",   23, WHITE,  WIDTH // 2, 185)
        draw_text(screen, f"Distance: {result['distance']} m", 23, WHITE, WIDTH // 2, 225)
        draw_text(screen, f"Coins: {result['coins']}",   23, WHITE,  WIDTH // 2, 265)
        draw_text(screen, f"Player: {result['name']}",   20, YELLOW, WIDTH // 2, 320)

        retry.draw(screen)
        menu.draw(screen)
        pygame.display.update()
        clock.tick(120)