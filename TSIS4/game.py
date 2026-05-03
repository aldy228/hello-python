"""
snake.py — Main file for the Snake TSIS3 game.
Contains all game logic, rendering, and screen management in one class: SnakeGame.

Architecture: instead of a separate main.py, everything lives inside SnakeGame.
The current screen is tracked by self.screen_name (a string like "menu", "playing",
"game_over", etc.) — the run() method routes to the correct screen each frame.
"""

import json
import os
import random
import sys

import pygame

from db import create_tables, get_personal_best, get_top_10, save_result


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

WIDTH       = 720    # window width in pixels
HEIGHT      = 480    # window height in pixels
BLOCK       = 20     # size of each grid cell in pixels (snake body, food, obstacles)
START_SPEED = 8      # initial game speed (frames per second for snake movement)

# Color palette
BLACK      = (15,  15,  18)
WHITE      = (240, 240, 240)
GRAY       = (55,  55,  60)
LIGHT_GRAY = (170, 170, 175)
DARK_GRAY  = (32,  32,  36)
GREEN      = (0,   200, 90)
BLUE       = (55,  140, 255)
RED        = (220, 45,  45)
DARK_RED   = (120, 15,  25)
YELLOW     = (245, 210, 70)
PURPLE     = (170, 90,  255)
CYAN       = (70,  220, 230)
ORANGE     = (255, 150, 50)
WALL_COLOR = (95,  95,  105)

# Paths
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
SOUNDS_DIR    = os.path.join(BASE_DIR, "sounds")


# ─────────────────────────────────────────────
#  BUTTON CLASS
# ─────────────────────────────────────────────

class Button:
    """
    A clickable rectangular button with a text label and hover effect.
    Requires a font to be passed to draw() — uses the game's existing font objects.
    """

    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        """
        Draw the button. Turns slightly lighter when the mouse hovers over it.
        The label is always centered inside the button rectangle.
        """
        mouse = pygame.mouse.get_pos()
        # Hover: lighter background; normal: darker background
        bg = (72, 72, 82) if self.rect.collidepoint(mouse) else (47, 47, 55)

        pygame.draw.rect(screen, bg,         self.rect, border_radius=12)  # filled background
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, 2, border_radius=12)  # border

        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        """Return True if this button was left-clicked in the given pygame event."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ─────────────────────────────────────────────
#  MAIN GAME CLASS
# ─────────────────────────────────────────────

class SnakeGame:
    """
    The entire Snake game in one class.
    Manages initialization, settings, sound, game state, rendering, and all screens.
    Navigation between screens is controlled by self.screen_name.
    """

    def __init__(self):
        # Initialize sound before pygame.init() to avoid audio glitches
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        try:
            pygame.mixer.init()
        except pygame.error:
            pass  # sound not available — continue without it

        pygame.display.set_caption("Snake TSIS3")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock  = pygame.time.Clock()

        # Font sizes for different UI elements
        self.big_font   = pygame.font.SysFont("Verdana", 42)  # titles
        self.font       = pygame.font.SysFont("Verdana", 22)  # main text, buttons
        self.small_font = pygame.font.SysFont("Verdana", 16)  # HUD and table rows
        self.tiny_font  = pygame.font.SysFont("Verdana", 13)  # hints and legend

        create_tables()              # make sure leaderboard.json exists
        self.settings = self.load_settings()
        self.sounds   = self.load_sounds()

        self.username        = ""        # typed by user on the menu screen
        self.screen_name     = "menu"    # controls which screen is shown
        self.game_over_saved = False     # prevents saving the same result twice

        self.start_music()
        self.reset_game()  # initialize all game state variables

    # ─────────────────────────────────────────────
    #  SETTINGS AND SOUND
    # ─────────────────────────────────────────────

    def load_settings(self):
        """
        Load settings from settings.json.
        If the file is missing or corrupted, returns the default values.
        Uses {**default, **data} so any key missing from the file gets its default value.
        """
        default = {
            "snake_color": [0, 200, 90],  # RGB list (not tuple — JSON doesn't have tuples)
            "grid":        True,
            "sound":       True
        }

        if not os.path.exists(SETTINGS_FILE):
            self.save_settings(default)
            return default

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            # Merge: default fills in any missing keys, data overrides the rest
            return {**default, **data}
        except Exception:
            return default  # file broken — reset to defaults silently

    def save_settings(self, data=None):
        """
        Write settings to settings.json.
        If no argument is given, saves self.settings (the current state).
        """
        if data is None:
            data = self.settings

        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_sounds(self):
        """
        Load sound effect files from the sounds/ folder.
        Returns a dict mapping name → pygame.mixer.Sound (or None if loading failed).
        None values are handled safely in play_sound().
        """
        sounds = {}
        files  = {
            "eat":   "eat.mp3",
            "death": "death.mp3",
            "move":  "move.mp3"
        }

        for key, filename in files.items():
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                try:
                    sounds[key] = pygame.mixer.Sound(path)
                    sounds[key].set_volume(0.75)
                except Exception:
                    sounds[key] = None  # failed to load — silently skip
            else:
                sounds[key] = None

        return sounds

    def start_music(self):
        """
        Start looping background music if the file exists and sound is enabled.
        play(-1) means loop forever.
        """
        music_path = os.path.join(SOUNDS_DIR, "music.mp3")
        if os.path.exists(music_path) and self.settings.get("sound", True):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(-1)   # -1 = loop indefinitely
            except Exception:
                pass

    def update_music_state(self):
        """
        Called when the sound toggle is changed in settings.
        Starts music if sound is now ON (and it wasn't already playing).
        Stops music if sound is now OFF.
        """
        if self.settings.get("sound", True):
            if not pygame.mixer.music.get_busy():
                self.start_music()
        else:
            pygame.mixer.music.stop()

    def play_sound(self, name):
        """
        Play a sound effect by name ("eat", "death", "move").
        Does nothing if sound is disabled or the sound failed to load.
        """
        if not self.settings.get("sound", True):
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(0.8)
            sound.play()

    # ─────────────────────────────────────────────
    #  SMALL HELPERS
    # ─────────────────────────────────────────────

    def draw_text(self, text, x, y, font=None, color=WHITE, center=False):
        """
        Render a string onto self.screen.
        center=True → (x,y) is the center of the text.
        center=False → (x,y) is the top-left corner.
        Defaults to self.font if no font is given.
        """
        if font is None:
            font = self.font

        surface = font.render(text, True, color)
        rect    = surface.get_rect()

        if center:
            rect.center  = (x, y)
        else:
            rect.topleft = (x, y)

        self.screen.blit(surface, rect)

    def random_cell(self):
        """
        Return a random [x, y] position aligned to the grid.
        x stays within the road boundary (1 block from each side).
        y stays below the HUD (top 60px) and above the bottom border.
        random.randrange gives multiples of BLOCK so positions snap to the grid.
        """
        x = random.randrange(1, WIDTH  // BLOCK - 1) * BLOCK
        y = random.randrange(3, HEIGHT // BLOCK - 1) * BLOCK
        return [x, y]

    def is_busy(self, pos):
        """
        Check if a grid cell is already occupied by the snake, an obstacle,
        the food, the poison, or a power-up.
        Used to avoid spawning two objects in the same cell.
        """
        return (
            pos in self.snake
            or pos in self.obstacles
            or pos == self.food_pos
            or pos == self.poison_pos
            or pos == self.power_pos
        )

    def free_cell(self):
        """
        Find a random grid cell that is not occupied by anything.
        Loops until a free cell is found (guaranteed to terminate in normal gameplay).
        """
        while True:
            pos = self.random_cell()
            if not self.is_busy(pos):
                return pos

    def free_cell_simple(self):
        """
        Like free_cell(), but only checks that the cell isn't part of the snake.
        Used during reset_game() before obstacles/food/poison are fully initialized.
        """
        while True:
            pos = self.random_cell()
            if pos not in self.snake:
                return pos

    # ─────────────────────────────────────────────
    #  GAME STATE
    # ─────────────────────────────────────────────

    def reset_game(self):
        """
        Initialize (or re-initialize) all game variables to their starting state.
        Called at the start of each new game run.
        The snake starts with 3 segments moving right near the center of the screen.
        """
        # Snake is a list of [x, y] positions; index 0 is the head
        self.snake     = [[120, 120], [100, 120], [80, 120]]
        self.direction      = "RIGHT"   # current movement direction
        self.next_direction = "RIGHT"   # buffered direction (applied on next move)

        self.score = 0
        self.level = 1
        self.speed = START_SPEED  # current game speed in FPS (increases with level)

        # Load the player's personal best to show in the HUD
        self.personal_best = get_personal_best(self.username) if self.username else 0

        self.obstacles = []  # list of [x, y] obstacle blocks (walls)

        # Food comes in 3 types: white (1pt), yellow (2pt), purple (3pt)
        # Each type has a lifetime — food respawns when it expires
        self.food_types = [
            {"color": WHITE,  "weight": 1, "life": 10000},  # disappears after 10s
            {"color": YELLOW, "weight": 2, "life": 8500},
            {"color": PURPLE, "weight": 3, "life": 7000}
        ]
        self.current_food = random.choice(self.food_types)
        self.food_pos     = self.free_cell_simple()
        self.food_time    = pygame.time.get_ticks()  # ms when food was last spawned

        self.poison_pos  = self.free_cell_simple()
        self.poison_time = pygame.time.get_ticks()

        # Power-up state
        self.power_pos        = None   # position of a power-up on the grid, or None
        self.power_type       = None   # "boost", "slow", or "shield"
        self.power_spawn_time = 0      # ms when the power-up appeared
        self.active_power     = None   # currently active power-up effect
        self.power_end_time   = 0      # ms when the active effect expires
        self.shield_ready     = False  # True when shield power-up is active

        self.game_over_saved = False   # reset so the result is saved on next game over

    # ─────────────────────────────────────────────
    #  SPAWN OBJECTS
    # ─────────────────────────────────────────────

    def spawn_food(self):
        """Pick a new random food type and place it in a free cell. Record the spawn time."""
        self.current_food = random.choice(self.food_types)
        self.food_pos     = self.free_cell()
        self.food_time    = pygame.time.get_ticks()

    def spawn_poison(self):
        """Place the poison in a new free cell and record the spawn time."""
        self.poison_pos  = self.free_cell()
        self.poison_time = pygame.time.get_ticks()

    def spawn_powerup(self):
        """
        Called every frame. Has a 2% chance of spawning a power-up if none is present.
        This keeps power-ups rare and prevents the screen from being cluttered.
        Power-up type is chosen randomly from: boost, slow, shield.
        """
        if self.power_pos is not None:
            return  # don't spawn a second one while one already exists

        if random.randint(1, 100) <= 2:  # 2% chance per frame
            self.power_type       = random.choice(["boost", "slow", "shield"])
            self.power_pos        = self.free_cell()
            self.power_spawn_time = pygame.time.get_ticks()

    def make_obstacles(self):
        """
        Generate wall obstacles starting from level 3.
        Obstacles come in three shapes: horizontal line, vertical line, or 2×2 square.
        Each shape is only placed if wall_is_safe() confirms it doesn't block the snake
        or overlap with food/poison/power-ups.
        The number of shapes grows with the level (capped at 6).
        """
        if self.level < 3:
            self.obstacles = []  # no obstacles in early levels
            return

        self.obstacles  = []
        shapes_count    = min(2 + self.level // 2, 6)  # more shapes at higher levels

        for _ in range(shapes_count):
            placed = False

            for _ in range(40):  # try up to 40 times to place each shape safely
                start      = self.random_cell()
                shape_type = random.choice(["line_h", "line_v", "square"])
                new_blocks = []

                if shape_type == "line_h":
                    length = random.randint(4, 7)
                    for i in range(length):
                        new_blocks.append([start[0] + i * BLOCK, start[1]])

                elif shape_type == "line_v":
                    length = random.randint(4, 6)
                    for i in range(length):
                        new_blocks.append([start[0], start[1] + i * BLOCK])

                else:  # "square" — a 2×2 block cluster
                    # Visually distinct from single-cell food/poison
                    new_blocks = [
                        [start[0],         start[1]],
                        [start[0] + BLOCK, start[1]],
                        [start[0],         start[1] + BLOCK],
                        [start[0] + BLOCK, start[1] + BLOCK]
                    ]

                if self.wall_is_safe(new_blocks):
                    self.obstacles.extend(new_blocks)
                    placed = True
                    break  # shape placed successfully, move to next one

            # If we couldn't place after 40 tries, skip this shape
            if not placed:
                continue

    def wall_is_safe(self, blocks):
        """
        Check whether a new wall shape can be safely placed.
        A wall is safe if ALL its blocks:
          - Stay within the playable area (not on the border or HUD)
          - Are not too close to the snake's head (within 4 cells)
          - Don't overlap with the snake body, existing obstacles, or pickup items
        Returns True only if every block passes all checks.
        """
        head = self.snake[0]

        for block in blocks:
            inside    = BLOCK <= block[0] < WIDTH - BLOCK and 60 <= block[1] < HEIGHT - BLOCK
            near_head = abs(block[0] - head[0]) <= BLOCK * 4 and abs(block[1] - head[1]) <= BLOCK * 4

            if not inside or near_head:
                return False
            if block in self.snake or block in self.obstacles:
                return False
            if block == self.food_pos or block == self.poison_pos or block == self.power_pos:
                return False

        return True

    # ─────────────────────────────────────────────
    #  MOVEMENT AND COLLISIONS
    # ─────────────────────────────────────────────

    def change_level_if_needed(self):
        """
        Check if the score has crossed a threshold that triggers the next level.
        Level = score // 50 + 1 — so every 50 points = one level up.
        On level-up: speed increases (capped at 15), new obstacles are generated,
        and any pickup that got covered by a new wall is relocated.
        """
        new_level = self.score // 50 + 1
        if new_level > self.level:
            self.level = new_level
            self.speed = min(self.speed + 0.8, 15)  # +0.8 FPS per level, max 15
            self.make_obstacles()

            # Relocate pickups if a new wall was placed on top of them
            if self.food_pos  in self.obstacles: self.spawn_food()
            if self.poison_pos in self.obstacles: self.spawn_poison()
            if self.power_pos  in self.obstacles:
                self.power_pos  = None
                self.power_type = None

    def handle_direction(self, event):
        """
        Update next_direction based on arrow key input.
        Prevents the snake from reversing directly into itself (e.g. can't go LEFT if moving RIGHT).
        next_direction is buffered and applied at the start of the next move_snake() call.
        Plays a move sound when the direction actually changes.
        """
        old_direction = self.next_direction

        if   event.key == pygame.K_UP    and self.direction != "DOWN":  self.next_direction = "UP"
        elif event.key == pygame.K_DOWN  and self.direction != "UP":    self.next_direction = "DOWN"
        elif event.key == pygame.K_LEFT  and self.direction != "RIGHT": self.next_direction = "LEFT"
        elif event.key == pygame.K_RIGHT and self.direction != "LEFT":  self.next_direction = "RIGHT"

        if self.next_direction != old_direction:
            self.play_sound("move")

    def move_snake(self):
        """
        Advance the snake by one step in the current direction.

        How snake movement works:
        1. Apply the buffered direction
        2. Compute the new head position (one BLOCK in the chosen direction)
        3. Insert the new head at the front of the snake list
        4. If the head lands on food: score increases, don't remove the tail (snake grows)
        5. If the head lands on poison: remove 2 tail segments (snake shrinks)
        6. Otherwise: remove the tail (snake moves forward without growing)
        7. Check for power-up collection
        """
        self.direction = self.next_direction  # commit the buffered direction
        head = self.snake[0].copy()           # copy current head position

        # Move the new head one cell in the current direction
        if   self.direction == "UP":    head[1] -= BLOCK
        elif self.direction == "DOWN":  head[1] += BLOCK
        elif self.direction == "LEFT":  head[0] -= BLOCK
        elif self.direction == "RIGHT": head[0] += BLOCK

        self.snake.insert(0, head)  # new head is now at index 0

        if head == self.food_pos:
            # Snake grows: don't remove tail; also increase score and respawn food
            self.score += self.current_food["weight"] * 10
            self.play_sound("eat")
            self.spawn_food()

        elif head == self.poison_pos:
            # Poison shrinks the snake by 2 segments
            # If the snake gets too short (≤1 segment), trigger game over
            self.play_sound("death")
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()  # remove from tail
            self.spawn_poison()
            if len(self.snake) <= 1:
                self.screen_name = "game_over"

        else:
            self.snake.pop()  # normal move: remove tail to keep length constant

        # Check if head landed on a power-up
        if self.power_pos and head == self.power_pos:
            self.collect_powerup()

    def collect_powerup(self):
        """
        Apply the collected power-up effect:
          boost:  speed +3 for 5 seconds (capped at 18)
          slow:   speed -3 for 5 seconds (floored at 5)
          shield: activates shield_ready flag — next fatal collision is absorbed
        Clears power_pos so a new one can eventually spawn.
        """
        now              = pygame.time.get_ticks()
        self.active_power = self.power_type
        self.power_pos    = None  # remove from the board
        self.play_sound("eat")

        if self.active_power == "boost":
            self.power_end_time = now + 5000
            self.speed          = min(self.speed + 3, 18)

        elif self.active_power == "slow":
            self.power_end_time = now + 5000
            self.speed          = max(5, self.speed - 3)

        elif self.active_power == "shield":
            self.shield_ready   = True
            self.power_end_time = 0  # shield doesn't expire — lasts until one hit

    def update_timers(self):
        """
        Called every frame to handle time-based events:
          - Expire food if it has been on screen longer than its lifetime
          - Expire poison every 10 seconds (forces the player to track it)
          - Expire uncollected power-ups after 8 seconds
          - Revert boost/slow speed changes when their duration ends
        """
        now = pygame.time.get_ticks()

        # Food expires based on its type's lifetime (7–10 seconds)
        if now - self.food_time > self.current_food["life"]:
            self.spawn_food()

        # Poison relocates every 10 seconds
        if now - self.poison_time > 10000:
            self.spawn_poison()

        # Power-up disappears if not collected within 8 seconds
        if self.power_pos and now - self.power_spawn_time > 8000:
            self.power_pos  = None
            self.power_type = None

        # Revert speed when boost or slow expires
        if self.active_power in ["boost", "slow"] and now >= self.power_end_time:
            if self.active_power == "boost":
                self.speed = max(START_SPEED, self.speed - 3)  # undo the +3
            elif self.active_power == "slow":
                self.speed += 3                                  # undo the -3
            self.active_power   = None
            self.power_end_time = 0

    def hit_something(self):
        """
        Check if the snake's head has collided with anything fatal:
          - Border (outside the playable area)
          - Its own body (self-collision)
          - A wall obstacle

        If shield is active: absorb the hit (teleport head to center, deactivate shield).
        Otherwise: play death sound and return True (triggers game over).
        Returns False if the snake is safe this frame.
        """
        head       = self.snake[0]
        hit_border = head[0] < BLOCK or head[0] >= WIDTH - BLOCK or head[1] < 60 or head[1] >= HEIGHT - BLOCK
        hit_self   = head in self.snake[1:]   # head overlaps any segment after index 0
        hit_wall   = head in self.obstacles

        if hit_border or hit_self or hit_wall:
            if self.shield_ready:
                # Shield absorbs the hit: reset head to center, deactivate shield
                self.shield_ready = False
                self.active_power = None
                self.snake[0]     = [WIDTH // 2, HEIGHT // 2]
                return False  # not game over

            self.play_sound("death")
            return True  # game over

        return False  # safe

    # ─────────────────────────────────────────────
    #  DRAWING
    # ─────────────────────────────────────────────

    def draw_grid(self):
        """
        Draw a subtle grid of lines over the canvas if grid is enabled in settings.
        Grid starts at y=60 (below the HUD bar).
        Lines are drawn in GRAY — dark enough to be subtle, visible on the black background.
        """
        if not self.settings.get("grid", True):
            return

        for x in range(0, WIDTH, BLOCK):
            pygame.draw.line(self.screen, GRAY, (x, 60), (x, HEIGHT))
        for y in range(60, HEIGHT, BLOCK):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw_obstacles(self):
        """
        Draw each obstacle block as a square with an X pattern (crossed lines).
        The X makes walls visually distinct from food (circle) and poison (diamond).
        """
        for block in self.obstacles:
            rect = pygame.Rect(block[0], block[1], BLOCK, BLOCK)
            pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=3)  # fill
            pygame.draw.rect(self.screen, DARK_GRAY,  rect, 2, border_radius=3)  # border
            # X cross — helps identify walls at a glance
            pygame.draw.line(self.screen, LIGHT_GRAY, rect.topleft,  rect.bottomright, 2)
            pygame.draw.line(self.screen, LIGHT_GRAY, rect.topright, rect.bottomleft,  2)

    def draw_food(self):
        """
        Draw food as a filled circle — color varies by food type (white/yellow/purple).
        Draw poison as a dark red diamond (polygon) with a white border.
        Different shapes make it immediately clear which is which without reading text.
        """
        # Food: circle centered in its grid cell
        center = (self.food_pos[0] + BLOCK // 2, self.food_pos[1] + BLOCK // 2)
        pygame.draw.circle(self.screen, self.current_food["color"], center, BLOCK // 2 - 2)

        # Poison: diamond shape (4 points: top, right, bottom, left of the cell)
        x, y = self.poison_pos
        points = [
            (x + BLOCK // 2, y + 2),          # top
            (x + BLOCK - 2,  y + BLOCK // 2), # right
            (x + BLOCK // 2, y + BLOCK - 2),  # bottom
            (x + 2,          y + BLOCK // 2)  # left
        ]
        pygame.draw.polygon(self.screen, DARK_RED, points)        # filled
        pygame.draw.polygon(self.screen, WHITE,    points, 1)     # outline

    def draw_powerup(self):
        """
        Draw the power-up as a colored rounded square with a letter inside:
          B (cyan)   = Boost
          S (blue)   = Slow
          H (orange) = sHield
        Only drawn if a power-up is currently on the board (power_pos is not None).
        """
        if not self.power_pos:
            return

        color = CYAN
        label = "B"
        if self.power_type == "slow":
            color, label = BLUE,   "S"
        elif self.power_type == "shield":
            color, label = ORANGE, "H"

        rect = pygame.Rect(self.power_pos[0], self.power_pos[1], BLOCK, BLOCK)
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        text = self.tiny_font.render(label, True, BLACK)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_game(self):
        """
        Render a complete game frame:
        1. Black background
        2. Dark HUD bar at the top (y=0 to y=60)
        3. Grid lines (if enabled)
        4. HUD text: score, level, personal best, active power-up
        5. Legend line (food/poison/wall visual guide)
        6. White border around the playable area
        7. Obstacles, food, poison, power-up
        8. Snake (head is blue; body uses the player's chosen color from settings)
        """
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WIDTH, 60))  # HUD background
        self.draw_grid()

        # HUD text
        self.draw_text(f"Score: {self.score}",          10,  10, self.small_font)
        self.draw_text(f"Level: {self.level}",          130, 10, self.small_font)
        self.draw_text(f"Best: {self.personal_best}",   240, 10, self.small_font)

        # Power-up status display
        if self.shield_ready:
            power_text = "Power: shield"
        elif self.active_power:
            left       = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
            power_text = f"Power: {self.active_power} {left}s"
        else:
            power_text = "Power: none"
        self.draw_text(power_text, 380, 10, self.small_font)

        # Visual legend so players know what each shape means
        self.draw_text("Food: circle   Poison: diamond   Wall: X block", 10, 35, self.tiny_font, LIGHT_GRAY)

        # Border around the playable area
        pygame.draw.rect(self.screen, WHITE, (0, 60, WIDTH, HEIGHT - 60), 3)

        self.draw_obstacles()
        self.draw_food()
        self.draw_powerup()

        # Draw the snake — head is always blue, body uses the player's chosen color
        snake_color = tuple(self.settings.get("snake_color", [0, 200, 90]))
        for i, block in enumerate(self.snake):
            color = BLUE if i == 0 else snake_color  # index 0 = head
            pygame.draw.rect(self.screen, color, (*block, BLOCK, BLOCK), border_radius=5)

    # ─────────────────────────────────────────────
    #  MAIN GAME LOOP
    # ─────────────────────────────────────────────

    def game_loop(self):
        """
        Run one complete game session from start to game over.
        Each iteration of the loop is one frame:
          1. Handle events (quit, direction keys)
          2. Move snake + spawn/update objects + check collisions
          3. Draw everything
          4. Cap frame rate with clock.tick(speed)

        The game speed (self.speed) directly controls how fast the snake moves
        because it's passed to clock.tick() — higher speed = more ticks per second.
        When game over is triggered, screen_name becomes "game_over" and the loop exits.
        """
        self.reset_game()
        self.personal_best = get_personal_best(self.username)
        self.screen_name   = "playing"

        while self.screen_name == "playing":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_direction(event)

            self.move_snake()
            self.spawn_powerup()
            self.update_timers()
            self.change_level_if_needed()

            if self.hit_something():
                self.screen_name = "game_over"

            self.draw_game()
            pygame.display.update()
            self.clock.tick(int(self.speed))  # speed controls how many frames per second

    # ─────────────────────────────────────────────
    #  SCREENS
    # ─────────────────────────────────────────────

    def menu_screen(self):
        """
        Main menu with username input and navigation buttons.
        The username is typed directly on this screen (no separate input dialog).
        Play is disabled if the username field is empty — a warning is shown instead.
        Pressing Enter while a name is typed also starts the game.
        """
        play        = Button("Play",        260, 170, 200, 45)
        leaderboard = Button("Leaderboard", 260, 225, 200, 45)
        settings    = Button("Settings",    260, 280, 200, 45)
        quit_btn    = Button("Quit",        260, 335, 200, 45)

        while self.screen_name == "menu":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]  # delete last character
                    elif event.key == pygame.K_RETURN and self.username.strip():
                        self.game_loop()  # Enter key starts the game
                    elif len(self.username) < 14 and event.unicode.isprintable():
                        self.username += event.unicode  # append typed character

                if play.clicked(event) and self.username.strip():
                    self.game_loop()
                if leaderboard.clicked(event):
                    self.screen_name = "leaderboard"
                if settings.clicked(event):
                    self.screen_name = "settings"
                if quit_btn.clicked(event):
                    pygame.quit()
                    sys.exit()

            # ── Draw the menu ──
            self.screen.fill(BLACK)
            self.draw_text("Snake", WIDTH // 2, 80, self.big_font, WHITE, center=True)
            self.draw_text("Enter username:", 245, 120, self.small_font)

            # Username input box
            pygame.draw.rect(self.screen, DARK_GRAY, (245, 140, 230, 30), border_radius=8)
            placeholder_color = GRAY if not self.username else WHITE
            self.draw_text(self.username or "type here", 255, 145, self.small_font, placeholder_color)

            # Show warning if username is empty and user tries to play
            if not self.username.strip():
                self.draw_text("username is required", 275, 390, self.small_font, RED)

            for button in [play, leaderboard, settings, quit_btn]:
                button.draw(self.screen, self.font)

            pygame.display.update()
            self.clock.tick(60)

    def game_over_screen(self):
        """
        Show the game over screen with final score, level, and personal best.
        Saves the result to leaderboard.json exactly once (game_over_saved prevents double-saving).
        Retry → starts a new game session.
        Main Menu → returns to the menu screen.
        """
        # Save result only once (guard against retry triggering another save)
        if not self.game_over_saved and self.username.strip():
            save_result(self.username, self.score, self.level)
            self.personal_best   = max(self.personal_best, self.score)  # update local best
            self.game_over_saved = True

        retry = Button("Retry",     260, 300, 200, 45)
        menu  = Button("Main Menu", 260, 355, 200, 45)

        while self.screen_name == "game_over":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if retry.clicked(event):
                    self.game_loop()   # start a fresh game without going to menu
                if menu.clicked(event):
                    self.screen_name = "menu"

            self.screen.fill(BLACK)
            self.draw_text("Game Over",                          WIDTH // 2, 110, self.big_font, RED,   center=True)
            self.draw_text(f"Score: {self.score}",               WIDTH // 2, 180, self.font,     WHITE, center=True)
            self.draw_text(f"Level reached: {self.level}",       WIDTH // 2, 215, self.font,     WHITE, center=True)
            self.draw_text(f"Personal best: {self.personal_best}", WIDTH // 2, 250, self.font,   WHITE, center=True)
            retry.draw(self.screen, self.font)
            menu.draw(self.screen, self.font)
            pygame.display.update()
            self.clock.tick(60)

    def leaderboard_screen(self):
        """
        Display the top 10 scores from leaderboard.json.
        get_top_10() returns tuples: (username, score, level_reached, played_at).
        Each row is formatted with fixed-width fields using f-string alignment (:<N).
        """
        back = Button("Back", 30, 415, 140, 40)

        while self.screen_name == "leaderboard":
            rows = get_top_10()  # reload every frame so new entries appear immediately

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if back.clicked(event):
                    self.screen_name = "menu"

            self.screen.fill(BLACK)
            self.draw_text("Leaderboard", WIDTH // 2, 45, self.big_font, WHITE, center=True)
            self.draw_text("Rank   Username        Score   Level   Date", 60, 105, self.small_font, YELLOW)

            if not rows:
                self.draw_text("No saved results yet", WIDTH // 2, 190, self.font, GRAY, center=True)

            for i, row in enumerate(rows):
                username, score, level, date = row  # unpack the tuple
                # Left-align each column with fixed width for a table-like appearance
                line = f"{i + 1:<6} {username:<14} {score:<7} {level:<7} {date}"
                self.draw_text(line, 60, 140 + i * 25, self.small_font)

            back.draw(self.screen, self.font)
            pygame.display.update()
            self.clock.tick(30)  # 30 FPS is enough for a static screen

    def settings_screen(self):
        """
        Settings screen with three toggleable options:
          Grid overlay: show/hide grid lines during gameplay
          Sound:        enable/disable music and sound effects
          Snake color:  cycle through 5 preset colors

        Changes are applied immediately but only written to disk when "Save & Back" is clicked.
        The color preview square shows the current snake color as a colored rectangle.
        """
        grid_btn  = Button("Toggle", 445, 135, 150, 42)
        sound_btn = Button("Toggle", 445, 195, 150, 42)
        color_btn = Button("Change", 445, 255, 150, 42)
        save_btn  = Button("Save & Back", 245, 365, 230, 45)

        # Available snake colors as RGB lists
        colors = [
            [0,   200, 90],   # green (default)
            [255, 120, 120],  # pink
            [80,  180, 255],  # light blue
            [220, 120, 255],  # purple
            [255, 210, 70]    # yellow
        ]

        while self.screen_name == "settings":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if grid_btn.clicked(event):
                    self.settings["grid"] = not self.settings.get("grid", True)

                if sound_btn.clicked(event):
                    self.settings["sound"] = not self.settings.get("sound", True)
                    self.update_music_state()  # start or stop music immediately

                if color_btn.clicked(event):
                    # Cycle to the next color, wrapping around with %
                    current = self.settings.get("snake_color", colors[0])
                    index   = colors.index(current) if current in colors else 0
                    self.settings["snake_color"] = colors[(index + 1) % len(colors)]

                if save_btn.clicked(event):
                    self.save_settings()      # write to settings.json
                    self.screen_name = "menu"

            # ── Draw the settings screen ──
            self.screen.fill(BLACK)
            self.draw_text("Settings", WIDTH // 2, 70, self.big_font, WHITE, center=True)

            # Grid row
            self.draw_text("Grid overlay", 125, 143, self.font)
            on_off_color = GREEN if self.settings.get("grid",  True) else RED
            self.draw_text("ON" if self.settings.get("grid", True) else "OFF", 315, 143, self.font, on_off_color)
            grid_btn.draw(self.screen, self.font)

            # Sound row
            self.draw_text("Sound", 125, 203, self.font)
            on_off_color = GREEN if self.settings.get("sound", True) else RED
            self.draw_text("ON" if self.settings.get("sound", True) else "OFF", 315, 203, self.font, on_off_color)
            sound_btn.draw(self.screen, self.font)

            # Color row — shows a colored square preview next to the button
            self.draw_text("Snake color", 125, 263, self.font)
            snake_color = tuple(self.settings.get("snake_color", [0, 200, 90]))
            pygame.draw.rect(self.screen, snake_color, (315, 258, 42, 42), border_radius=8)  # color preview
            pygame.draw.rect(self.screen, WHITE,       (315, 258, 42, 42), 2, border_radius=8)  # border
            color_btn.draw(self.screen, self.font)

            save_btn.draw(self.screen, self.font)
            pygame.display.update()
            self.clock.tick(60)

    # ─────────────────────────────────────────────
    #  ENTRY POINT
    # ─────────────────────────────────────────────

    def run(self):
        """
        Top-level loop that routes to the correct screen based on self.screen_name.
        Each screen function runs its own inner loop and returns when screen_name changes.
        This continues indefinitely — the game only exits via pygame.quit() + sys.exit()
        called inside the individual screen functions.
        """
        while True:
            if   self.screen_name == "menu":        self.menu_screen()
            elif self.screen_name == "playing":     self.game_loop()
            elif self.screen_name == "game_over":   self.game_over_screen()
            elif self.screen_name == "leaderboard": self.leaderboard_screen()
            elif self.screen_name == "settings":    self.settings_screen()


# ─────────────────────────────────────────────
#  START THE GAME
# ─────────────────────────────────────────────

if __name__ == "__main__":
    SnakeGame().run()