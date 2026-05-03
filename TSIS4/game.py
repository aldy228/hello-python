import json
import os
import random
import sys

import pygame

from db import create_tables, get_personal_best, get_top_10, save_result


# -------------------- BASIC SETTINGS --------------------
WIDTH = 720
HEIGHT = 480
BLOCK = 20
START_SPEED = 8

BLACK = (15, 15, 18)
WHITE = (240, 240, 240)
GRAY = (55, 55, 60)
LIGHT_GRAY = (170, 170, 175)
DARK_GRAY = (32, 32, 36)
GREEN = (0, 200, 90)
BLUE = (55, 140, 255)
RED = (220, 45, 45)
DARK_RED = (120, 15, 25)
YELLOW = (245, 210, 70)
PURPLE = (170, 90, 255)
CYAN = (70, 220, 230)
ORANGE = (255, 150, 50)
WALL_COLOR = (95, 95, 105)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        bg = (72, 72, 82) if self.rect.collidepoint(mouse) else (47, 47, 55)
        pygame.draw.rect(screen, bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, 2, border_radius=12)

        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class SnakeGame:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        pygame.display.set_caption("Snake TSIS3")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.big_font = pygame.font.SysFont("Verdana", 42)
        self.font = pygame.font.SysFont("Verdana", 22)
        self.small_font = pygame.font.SysFont("Verdana", 16)
        self.tiny_font = pygame.font.SysFont("Verdana", 13)

        create_tables()
        self.settings = self.load_settings()
        self.sounds = self.load_sounds()

        self.username = ""
        self.screen_name = "menu"
        self.game_over_saved = False

        self.start_music()
        self.reset_game()

    # -------------------- SETTINGS AND SOUND --------------------
    def load_settings(self):
        default = {
            "snake_color": [0, 200, 90],
            "grid": True,
            "sound": True
        }

        if not os.path.exists(SETTINGS_FILE):
            self.save_settings(default)
            return default

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            return {**default, **data}
        except Exception:
            return default

    def save_settings(self, data=None):
        if data is None:
            data = self.settings

        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_sounds(self):
        sounds = {}
        files = {
            "eat": "eat.mp3",
            "death": "death.mp3",
            "move": "move.mp3"
        }

        for key, filename in files.items():
            path = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(path):
                try:
                    sounds[key] = pygame.mixer.Sound(path)
                    sounds[key].set_volume(0.75)
                except Exception:
                    sounds[key] = None
            else:
                sounds[key] = None

        return sounds

    def start_music(self):
        music_path = os.path.join(SOUNDS_DIR, "music.mp3")
        if os.path.exists(music_path) and self.settings.get("sound", True):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.45)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def update_music_state(self):
        if self.settings.get("sound", True):
            if not pygame.mixer.music.get_busy():
                self.start_music()
        else:
            pygame.mixer.music.stop()

    def play_sound(self, name):
        if not self.settings.get("sound", True):
            return
        sound = self.sounds.get(name)
        if sound:
            sound.set_volume(0.8)
            sound.play()

    # -------------------- SMALL HELPERS --------------------
    def draw_text(self, text, x, y, font=None, color=WHITE, center=False):
        if font is None:
            font = self.font

        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def random_cell(self):
        x = random.randrange(1, WIDTH // BLOCK - 1) * BLOCK
        y = random.randrange(3, HEIGHT // BLOCK - 1) * BLOCK
        return [x, y]

    def is_busy(self, pos):
        return (
            pos in self.snake
            or pos in self.obstacles
            or pos == self.food_pos
            or pos == self.poison_pos
            or pos == self.power_pos
        )

    def free_cell(self):
        while True:
            pos = self.random_cell()
            if not self.is_busy(pos):
                return pos

    def free_cell_simple(self):
        while True:
            pos = self.random_cell()
            if pos not in self.snake:
                return pos

    # -------------------- GAME STATE --------------------
    def reset_game(self):
        self.snake = [[120, 120], [100, 120], [80, 120]]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"

        self.score = 0
        self.level = 1
        self.speed = START_SPEED
        self.personal_best = get_personal_best(self.username) if self.username else 0

        self.obstacles = []

        self.food_types = [
            {"color": WHITE, "weight": 1, "life": 10000},
            {"color": YELLOW, "weight": 2, "life": 8500},
            {"color": PURPLE, "weight": 3, "life": 7000}
        ]
        self.current_food = random.choice(self.food_types)
        self.food_pos = self.free_cell_simple()
        self.food_time = pygame.time.get_ticks()

        self.poison_pos = self.free_cell_simple()
        self.poison_time = pygame.time.get_ticks()

        self.power_pos = None
        self.power_type = None
        self.power_spawn_time = 0
        self.active_power = None
        self.power_end_time = 0
        self.shield_ready = False

        self.game_over_saved = False

    # -------------------- SPAWN OBJECTS --------------------
    def spawn_food(self):
        self.current_food = random.choice(self.food_types)
        self.food_pos = self.free_cell()
        self.food_time = pygame.time.get_ticks()

    def spawn_poison(self):
        self.poison_pos = self.free_cell()
        self.poison_time = pygame.time.get_ticks()

    def spawn_powerup(self):
        if self.power_pos is not None:
            return

        # Small chance every frame. This keeps power-ups rare and readable.
        if random.randint(1, 100) <= 2:
            self.power_type = random.choice(["boost", "slow", "shield"])
            self.power_pos = self.free_cell()
            self.power_spawn_time = pygame.time.get_ticks()

    def make_obstacles(self):
        """
        Obstacles start from level 3.
        They are made from several connected blocks, so they look like real walls,
        not like food or poison.
        """
        if self.level < 3:
            self.obstacles = []
            return

        self.obstacles = []
        shapes_count = min(2 + self.level // 2, 6)

        for _ in range(shapes_count):
            placed = False

            for _ in range(40):
                start = self.random_cell()
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

                else:
                    # 2x2 block wall. This is visually different from one-cell food.
                    new_blocks = [
                        [start[0], start[1]],
                        [start[0] + BLOCK, start[1]],
                        [start[0], start[1] + BLOCK],
                        [start[0] + BLOCK, start[1] + BLOCK]
                    ]

                if self.wall_is_safe(new_blocks):
                    self.obstacles.extend(new_blocks)
                    placed = True
                    break

            if not placed:
                continue

    def wall_is_safe(self, blocks):
        head = self.snake[0]
        for block in blocks:
            inside = BLOCK <= block[0] < WIDTH - BLOCK and 60 <= block[1] < HEIGHT - BLOCK
            near_head = abs(block[0] - head[0]) <= BLOCK * 4 and abs(block[1] - head[1]) <= BLOCK * 4

            if not inside or near_head:
                return False
            if block in self.snake or block in self.obstacles:
                return False
            if block == self.food_pos or block == self.poison_pos or block == self.power_pos:
                return False

        return True

    # -------------------- MOVEMENT AND COLLISIONS --------------------
    def change_level_if_needed(self):
        new_level = self.score // 50 + 1
        if new_level > self.level:
            self.level = new_level
            self.speed = min(self.speed + 0.8, 15)
            self.make_obstacles()

            # After new walls appear, relocate objects if a wall covers them.
            if self.food_pos in self.obstacles:
                self.spawn_food()
            if self.poison_pos in self.obstacles:
                self.spawn_poison()
            if self.power_pos in self.obstacles:
                self.power_pos = None
                self.power_type = None

    def handle_direction(self, event):
        old_direction = self.next_direction

        if event.key == pygame.K_UP and self.direction != "DOWN":
            self.next_direction = "UP"
        elif event.key == pygame.K_DOWN and self.direction != "UP":
            self.next_direction = "DOWN"
        elif event.key == pygame.K_LEFT and self.direction != "RIGHT":
            self.next_direction = "LEFT"
        elif event.key == pygame.K_RIGHT and self.direction != "LEFT":
            self.next_direction = "RIGHT"

        if self.next_direction != old_direction:
            self.play_sound("move")

    def move_snake(self):
        self.direction = self.next_direction
        head = self.snake[0].copy()

        if self.direction == "UP":
            head[1] -= BLOCK
        elif self.direction == "DOWN":
            head[1] += BLOCK
        elif self.direction == "LEFT":
            head[0] -= BLOCK
        elif self.direction == "RIGHT":
            head[0] += BLOCK

        self.snake.insert(0, head)

        if head == self.food_pos:
            self.score += self.current_food["weight"] * 10
            self.play_sound("eat")
            self.spawn_food()

        elif head == self.poison_pos:
            # Poison removes two segments. If the snake becomes too short, game over.
            self.play_sound("death")
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            self.spawn_poison()
            if len(self.snake) <= 1:
                self.screen_name = "game_over"

        else:
            self.snake.pop()

        if self.power_pos and head == self.power_pos:
            self.collect_powerup()

    def collect_powerup(self):
        now = pygame.time.get_ticks()
        self.active_power = self.power_type
        self.power_pos = None
        self.play_sound("eat")

        if self.active_power == "boost":
            self.power_end_time = now + 5000
            self.speed = min(self.speed + 3, 18)
        elif self.active_power == "slow":
            self.power_end_time = now + 5000
            self.speed = max(5, self.speed - 3)
        elif self.active_power == "shield":
            self.shield_ready = True
            self.power_end_time = 0

    def update_timers(self):
        now = pygame.time.get_ticks()

        if now - self.food_time > self.current_food["life"]:
            self.spawn_food()

        if now - self.poison_time > 10000:
            self.spawn_poison()

        if self.power_pos and now - self.power_spawn_time > 8000:
            self.power_pos = None
            self.power_type = None

        if self.active_power in ["boost", "slow"] and now >= self.power_end_time:
            if self.active_power == "boost":
                self.speed = max(START_SPEED, self.speed - 3)
            elif self.active_power == "slow":
                self.speed += 3
            self.active_power = None
            self.power_end_time = 0

    def hit_something(self):
        head = self.snake[0]
        hit_border = head[0] < BLOCK or head[0] >= WIDTH - BLOCK or head[1] < 60 or head[1] >= HEIGHT - BLOCK
        hit_self = head in self.snake[1:]
        hit_wall = head in self.obstacles

        if hit_border or hit_self or hit_wall:
            if self.shield_ready:
                self.shield_ready = False
                self.active_power = None
                self.snake[0] = [WIDTH // 2, HEIGHT // 2]
                return False

            self.play_sound("death")
            return True

        return False

    # -------------------- DRAW GAME --------------------
    def draw_grid(self):
        if not self.settings.get("grid", True):
            return

        for x in range(0, WIDTH, BLOCK):
            pygame.draw.line(self.screen, GRAY, (x, 60), (x, HEIGHT))
        for y in range(60, HEIGHT, BLOCK):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

    def draw_obstacles(self):
        for block in self.obstacles:
            rect = pygame.Rect(block[0], block[1], BLOCK, BLOCK)
            pygame.draw.rect(self.screen, WALL_COLOR, rect, border_radius=3)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2, border_radius=3)
            pygame.draw.line(self.screen, LIGHT_GRAY, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, LIGHT_GRAY, rect.topright, rect.bottomleft, 2)

    def draw_food(self):
        # Normal food is a circle.
        center = (self.food_pos[0] + BLOCK // 2, self.food_pos[1] + BLOCK // 2)
        pygame.draw.circle(self.screen, self.current_food["color"], center, BLOCK // 2 - 2)

        # Poison is a dark red diamond, so it does not look like normal food.
        x, y = self.poison_pos
        points = [
            (x + BLOCK // 2, y + 2),
            (x + BLOCK - 2, y + BLOCK // 2),
            (x + BLOCK // 2, y + BLOCK - 2),
            (x + 2, y + BLOCK // 2)
        ]
        pygame.draw.polygon(self.screen, DARK_RED, points)
        pygame.draw.polygon(self.screen, WHITE, points, 1)

    def draw_powerup(self):
        if not self.power_pos:
            return

        color = CYAN
        label = "B"
        if self.power_type == "slow":
            color = BLUE
            label = "S"
        elif self.power_type == "shield":
            color = ORANGE
            label = "H"

        rect = pygame.Rect(self.power_pos[0], self.power_pos[1], BLOCK, BLOCK)
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        text = self.tiny_font.render(label, True, BLACK)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_game(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WIDTH, 60))
        self.draw_grid()

        self.draw_text(f"Score: {self.score}", 10, 10, self.small_font)
        self.draw_text(f"Level: {self.level}", 130, 10, self.small_font)
        self.draw_text(f"Best: {self.personal_best}", 240, 10, self.small_font)

        power_text = "Power: none"
        if self.shield_ready:
            power_text = "Power: shield"
        elif self.active_power:
            left = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
            power_text = f"Power: {self.active_power} {left}s"
        self.draw_text(power_text, 380, 10, self.small_font)

        self.draw_text("Food: circle   Poison: diamond   Wall: X block", 10, 35, self.tiny_font, LIGHT_GRAY)
        pygame.draw.rect(self.screen, WHITE, (0, 60, WIDTH, HEIGHT - 60), 3)

        self.draw_obstacles()
        self.draw_food()
        self.draw_powerup()

        snake_color = tuple(self.settings.get("snake_color", [0, 200, 90]))
        for i, block in enumerate(self.snake):
            color = BLUE if i == 0 else snake_color
            pygame.draw.rect(self.screen, color, (*block, BLOCK, BLOCK), border_radius=5)

    # -------------------- MAIN GAME LOOP --------------------
    def game_loop(self):
        self.reset_game()
        self.personal_best = get_personal_best(self.username)
        self.screen_name = "playing"

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
            self.clock.tick(int(self.speed))

    # -------------------- SCREENS --------------------
    def menu_screen(self):
        play = Button("Play", 260, 170, 200, 45)
        leaderboard = Button("Leaderboard", 260, 225, 200, 45)
        settings = Button("Settings", 260, 280, 200, 45)
        quit_btn = Button("Quit", 260, 335, 200, 45)

        while self.screen_name == "menu":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN and self.username.strip():
                        self.game_loop()
                    elif len(self.username) < 14 and event.unicode.isprintable():
                        self.username += event.unicode

                if play.clicked(event) and self.username.strip():
                    self.game_loop()
                if leaderboard.clicked(event):
                    self.screen_name = "leaderboard"
                if settings.clicked(event):
                    self.screen_name = "settings"
                if quit_btn.clicked(event):
                    pygame.quit()
                    sys.exit()

            self.screen.fill(BLACK)
            self.draw_text("Snake", WIDTH // 2, 80, self.big_font, WHITE, center=True)
            self.draw_text("Enter username:", 245, 120, self.small_font)
            pygame.draw.rect(self.screen, DARK_GRAY, (245, 140, 230, 30), border_radius=8)
            placeholder_color = GRAY if not self.username else WHITE
            self.draw_text(self.username or "type here", 255, 145, self.small_font, placeholder_color)

            if not self.username.strip():
                self.draw_text("username is required", 275, 390, self.small_font, RED)

            for button in [play, leaderboard, settings, quit_btn]:
                button.draw(self.screen, self.font)

            pygame.display.update()
            self.clock.tick(60)

    def game_over_screen(self):
        if not self.game_over_saved and self.username.strip():
            save_result(self.username, self.score, self.level)
            self.personal_best = max(self.personal_best, self.score)
            self.game_over_saved = True

        retry = Button("Retry", 260, 300, 200, 45)
        menu = Button("Main Menu", 260, 355, 200, 45)

        while self.screen_name == "game_over":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if retry.clicked(event):
                    self.game_loop()
                if menu.clicked(event):
                    self.screen_name = "menu"

            self.screen.fill(BLACK)
            self.draw_text("Game Over", WIDTH // 2, 110, self.big_font, RED, center=True)
            self.draw_text(f"Score: {self.score}", WIDTH // 2, 180, self.font, WHITE, center=True)
            self.draw_text(f"Level reached: {self.level}", WIDTH // 2, 215, self.font, WHITE, center=True)
            self.draw_text(f"Personal best: {self.personal_best}", WIDTH // 2, 250, self.font, WHITE, center=True)
            retry.draw(self.screen, self.font)
            menu.draw(self.screen, self.font)
            pygame.display.update()
            self.clock.tick(60)

    def leaderboard_screen(self):
        back = Button("Back", 30, 415, 140, 40)

        while self.screen_name == "leaderboard":
            rows = get_top_10()

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
                username, score, level, date = row
                line = f"{i + 1:<6} {username:<14} {score:<7} {level:<7} {date}"
                self.draw_text(line, 60, 140 + i * 25, self.small_font)

            back.draw(self.screen, self.font)
            pygame.display.update()
            self.clock.tick(30)

    def settings_screen(self):
        grid_btn = Button("Toggle", 445, 135, 150, 42)
        sound_btn = Button("Toggle", 445, 195, 150, 42)
        color_btn = Button("Change", 445, 255, 150, 42)
        save_btn = Button("Save & Back", 245, 365, 230, 45)
        colors = [
            [0, 200, 90],
            [255, 120, 120],
            [80, 180, 255],
            [220, 120, 255],
            [255, 210, 70]
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
                    self.update_music_state()

                if color_btn.clicked(event):
                    current = self.settings.get("snake_color", colors[0])
                    index = colors.index(current) if current in colors else 0
                    self.settings["snake_color"] = colors[(index + 1) % len(colors)]

                if save_btn.clicked(event):
                    self.save_settings()
                    self.screen_name = "menu"

            self.screen.fill(BLACK)
            self.draw_text("Settings", WIDTH // 2, 70, self.big_font, WHITE, center=True)

            # Clean two-column layout: label on the left, button on the right.
            self.draw_text("Grid overlay", 125, 143, self.font)
            self.draw_text("ON" if self.settings.get("grid", True) else "OFF", 315, 143, self.font, GREEN if self.settings.get("grid", True) else RED)
            grid_btn.draw(self.screen, self.font)

            self.draw_text("Sound", 125, 203, self.font)
            self.draw_text("ON" if self.settings.get("sound", True) else "OFF", 315, 203, self.font, GREEN if self.settings.get("sound", True) else RED)
            sound_btn.draw(self.screen, self.font)

            self.draw_text("Snake color", 125, 263, self.font)
            pygame.draw.rect(self.screen, tuple(self.settings.get("snake_color", [0, 200, 90])), (315, 258, 42, 42), border_radius=8)
            pygame.draw.rect(self.screen, WHITE, (315, 258, 42, 42), 2, border_radius=8)
            color_btn.draw(self.screen, self.font)

            save_btn.draw(self.screen, self.font)

            pygame.display.update()
            self.clock.tick(60)

    def run(self):
        while True:
            if self.screen_name == "menu":
                self.menu_screen()
            elif self.screen_name == "playing":
                self.game_loop()
            elif self.screen_name == "game_over":
                self.game_over_screen()
            elif self.screen_name == "leaderboard":
                self.leaderboard_screen()
            elif self.screen_name == "settings":
                self.settings_screen()