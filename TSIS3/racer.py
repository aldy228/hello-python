"""
racer.py — Core gameplay for the TSIS3 Racer game.
Contains all sprite classes (Player, TrafficCar, Coin, Obstacle, PowerUp, RoadEvent)
and the RacerGame class which runs the main game loop.

Architecture: each object on screen is a pygame Sprite — it has an image and a rect.
All sprites are added to sprite Groups which handle drawing and update calls in bulk.
"""

import os
import random
import pygame
from persistence import add_score

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

WIDTH           = 400
HEIGHT          = 600
FPS             = 60
FINISH_DISTANCE = 3000   # meters — reach this to win (or trigger game over as a win)

# Color palette
WHITE  = (255, 255, 255)
BLACK  = (20,  20,  20)
GRAY   = (120, 120, 120)
RED    = (220, 50,  50)
BLUE   = (40,  160, 255)
GREEN  = (60,  180, 80)
YELLOW = (245, 210, 60)
ORANGE = (245, 130, 40)
PURPLE = (150, 80,  220)
CYAN   = (60,  220, 220)
BROWN  = (70,  45,  35)

# Asset paths
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Road layout — the road runs between x=40 and x=360
# LANES are the x-centers of the three driveable lanes
ROAD_LEFT  = 40
ROAD_RIGHT = 360
LANES      = [95, 200, 305]  # left lane, center lane, right lane

# Maps color name (from settings) to the sprite filename
CAR_IMAGES = {
    "Orange": "Player_orange.png",
    "Blue":   "Player_blue.png",
    "Yellow": "Player_yellow.png",
    "Green":  "Player_green.png",
    "Purple": "Player_purple.png",
}

# Difficulty settings: base speed, and spawn intervals (in frames) for each object type
# Lower interval = more frequent spawns = harder
DIFFICULTY = {
    "Easy":   {"speed": 4, "traffic": 120, "obstacle": 170, "event": 320},
    "Normal": {"speed": 5, "traffic":  90, "obstacle": 130, "event": 260},
    "Hard":   {"speed": 6, "traffic":  65, "obstacle": 100, "event": 210},
}


# ─────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────

def draw_text(surface, text, size, color, x, y, center=False):
    """Render text onto a surface. center=False means top-left positioning."""
    font  = pygame.font.SysFont("Verdana", size)
    image = font.render(text, True, color)
    rect  = image.get_rect()
    if center:
        rect.center  = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)


def load_image(filename, size=None):
    """
    Load an image from the assets folder.
    convert_alpha() optimizes it for fast blitting with transparency.
    smoothscale() resizes with anti-aliasing for better quality.
    """
    path  = os.path.join(ASSET_DIR, filename)
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image


def load_player_car(color_name):
    """Load the player car sprite matching the chosen color from settings."""
    filename = CAR_IMAGES.get(color_name, CAR_IMAGES["Orange"])  # default to Orange
    return load_image(filename, (44, 96))  # all car sprites scaled to 44×96 px


def safe_spawn_y(player_rect):
    """
    Return a random y position above the top of the screen for spawning objects.
    If the player is near the top, spawn further up to avoid instant collisions.
    Objects scroll downward at road speed and enter the visible area naturally.
    """
    if player_rect.top < 160:
        return random.randint(-360, -100)  # spawn further up
    return random.randint(-520, -120)       # normal spawn range


# ─────────────────────────────────────────────
#  SPRITE CLASSES
# ─────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    """
    The player's car — controlled with LEFT and RIGHT arrow keys.
    Inherits from pygame.sprite.Sprite, which gives it .image and .rect.
    The player stays at a fixed y position; the road scrolls under them.
    """

    def __init__(self, color_name):
        super().__init__()
        self.image = load_player_car(color_name)
        # Start near the bottom-center of the screen
        self.rect  = self.image.get_rect(center=(200, 500))
        self.speed = 6  # horizontal movement speed in pixels per frame

    def update(self):
        """
        Called every frame. Moves the car left/right based on held keys.
        Clamped to ROAD_LEFT and ROAD_RIGHT so the car can't leave the road.
        UP/DOWN keys are intentionally ignored — the player never moves vertically.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]  and self.rect.left  > ROAD_LEFT:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.x += self.speed


class TrafficCar(pygame.sprite.Sprite):
    """
    An enemy/traffic car that scrolls downward toward the player.
    Spawns above the screen in a random lane and disappears when it passes the bottom.
    Speed increases with distance traveled (set by RacerGame when spawning).
    """

    def __init__(self, speed, player_rect):
        super().__init__()
        self.image      = load_image("Enemy.png", (48, 93))
        self.rect       = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)        # random lane
        self.rect.y       = safe_spawn_y(player_rect)   # above the screen
        self.speed        = speed

    def update(self):
        self.rect.y += self.speed  # scroll down
        if self.rect.top > HEIGHT:
            self.kill()  # remove from all groups when off-screen (saves memory)


class Coin(pygame.sprite.Sprite):
    """
    A collectible coin drawn procedurally (no image file needed).
    Has a random value of 1, 2, or 3 — shown as a number on the coin.
    Larger value = larger coin sprite.
    """

    def __init__(self, player_rect):
        super().__init__()
        self.value = random.choice([1, 2, 3])
        size       = 16 + self.value * 4  # coin size grows with value

        # Draw the coin onto a transparent Surface
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (size // 2, size // 2), size // 2)          # fill
        pygame.draw.circle(self.image, ORANGE, (size // 2, size // 2), size // 2, 3)       # border
        # Draw the value number centered on the coin
        font = pygame.font.SysFont("Verdana", 12, bold=True)
        txt  = font.render(str(self.value), True, BLACK)
        self.image.blit(txt, txt.get_rect(center=(size // 2, size // 2)))

        self.rect           = self.image.get_rect()
        self.rect.centerx   = random.choice(LANES)
        self.rect.y         = safe_spawn_y(player_rect)
        self.speed          = 4  # fixed speed, slower than traffic

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    """
    A static road hazard — three types, all drawn procedurally:
      - "barrier":  orange road barrier (causes crash)
      - "oil":      oil slick ellipse (causes slow)
      - "pothole":  brown/black hole (causes crash)
    The type determines both appearance and behavior (handled in RacerGame.update).
    """

    def __init__(self, obstacle_type, speed, player_rect):
        super().__init__()
        self.type  = obstacle_type
        self.speed = speed

        # Draw different visuals depending on type
        if self.type == "barrier":
            self.image = pygame.Surface((75, 25), pygame.SRCALPHA)
            pygame.draw.rect(self.image, ORANGE, (0, 0, 75, 25), border_radius=4)
            pygame.draw.line(self.image, WHITE, (6, 20), (68, 4), 4)  # diagonal stripe

        elif self.type == "oil":
            self.image = pygame.Surface((55, 35), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, BLACK,      (0,  0,  55, 35))  # outer pool
            pygame.draw.ellipse(self.image, (70,70,70), (12, 8,  25, 12))  # sheen highlight

        else:  # "pothole"
            self.image = pygame.Surface((50, 34), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, BROWN, (0, 0,  50, 34))  # dirt surround
            pygame.draw.ellipse(self.image, BLACK, (9, 8,  30, 15))  # dark hole

        self.rect         = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y       = safe_spawn_y(player_rect)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    """
    A collectible power-up — three types, each drawn as a colored circle with a letter:
      - "Nitro"  (N, cyan):   temporary speed boost for 4 seconds
      - "Shield" (S, purple): absorbs one collision
      - "Repair" (R, green):  instantly removes one hazard from the road

    Power-ups expire after 6 seconds if not collected (self.timeout).
    """

    def __init__(self, kind, player_rect):
        super().__init__()
        self.kind       = kind
        self.spawn_time = pygame.time.get_ticks()  # ms when this sprite was created
        self.timeout    = 6000  # disappears after 6 seconds if not collected

        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)

        # Color and letter vary by power-up type
        if kind == "Nitro":
            color, letter = CYAN,   "N"
        elif kind == "Shield":
            color, letter = PURPLE, "S"
        else:  # "Repair"
            color, letter = GREEN,  "R"

        pygame.draw.circle(self.image, color, (18, 18), 18)      # filled circle
        pygame.draw.circle(self.image, WHITE, (18, 18), 18, 2)   # white border
        font = pygame.font.SysFont("Verdana", 19, bold=True)
        text = font.render(letter, True, WHITE)
        self.image.blit(text, text.get_rect(center=(18, 17)))

        self.rect         = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y       = safe_spawn_y(player_rect)
        self.speed        = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
        # Also kill if the power-up has been on screen too long without being collected
        if pygame.time.get_ticks() - self.spawn_time > self.timeout:
            self.kill()


class RoadEvent(pygame.sprite.Sprite):
    """
    A special road feature — three types:
      - "speed_bump":    yellow bump — slows the player for 1.8 seconds
      - "nitro_strip":   cyan strip  — acts like a Nitro power-up on contact
      - "moving_barrier": orange barrier that bounces left/right across the road
    """

    def __init__(self, event_type, speed, player_rect):
        super().__init__()
        self.type  = event_type
        self.speed = speed

        if event_type == "speed_bump":
            self.image = pygame.Surface((90, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image,  YELLOW, (0, 0, 90, 20), border_radius=6)
            pygame.draw.line(self.image,  BLACK,  (10, 5),  (80, 5),  3)  # top stripe
            pygame.draw.line(self.image,  BLACK,  (10, 15), (80, 15), 3)  # bottom stripe

        elif event_type == "nitro_strip":
            self.image = pygame.Surface((75, 28), pygame.SRCALPHA)
            pygame.draw.rect(self.image,     CYAN,  (0, 0, 75, 28), border_radius=8)
            # Lightning bolt shape drawn as a filled polygon
            pygame.draw.polygon(self.image, WHITE,  [(10,22),(25,6),(25,16),(45,6),(31,22)])

        else:  # "moving_barrier"
            self.image = pygame.Surface((75, 25), pygame.SRCALPHA)
            pygame.draw.rect(self.image,  ORANGE, (0, 0, 75, 25), border_radius=4)
            pygame.draw.line(self.image,  WHITE,  (6, 20), (68, 4), 4)

        self.rect         = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y       = safe_spawn_y(player_rect)
        # Moving barriers bounce horizontally; direction is +2 or -2 px per frame
        self.direction    = random.choice([-2, 2])

    def update(self):
        self.rect.y += self.speed  # always scroll down

        # Moving barrier bounces left/right between road edges
        if self.type == "moving_barrier":
            self.rect.x += self.direction
            if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
                self.direction *= -1  # reverse direction on hitting a road edge

        if self.rect.top > HEIGHT:
            self.kill()


# ─────────────────────────────────────────────
#  MAIN GAME CLASS
# ─────────────────────────────────────────────

class RacerGame:
    """
    Manages the entire gameplay session: spawning, updating, collision detection,
    HUD drawing, and the game loop.

    The game ends when:
      - The player collides with a dangerous object (game_over = True, loss)
      - The player travels FINISH_DISTANCE meters (game_over = True, win)

    After the loop ends, the score is saved to the leaderboard and a result
    dictionary is returned to main.py for the game-over screen.
    """

    def __init__(self, screen, clock, settings, username):
        self.screen   = screen
        self.clock    = clock
        self.settings = settings
        self.username = username

        # Look up the difficulty config dict by name
        self.config     = DIFFICULTY[settings["difficulty"]]
        self.base_speed = self.config["speed"]

        # Background image — scrolled vertically to simulate road motion
        self.background = load_image("AnimatedStreet.png", (WIDTH, HEIGHT))
        self.bg_y       = 0  # current vertical offset of the background

        # Create the player sprite
        self.player = Player(settings["car_color"])

        # ── Sound ──
        self.crash_sound = None
        crash_path = os.path.join(ASSET_DIR, "crash.wav")
        if settings.get("sound", True) and os.path.exists(crash_path):
            try:
                self.crash_sound = pygame.mixer.Sound(crash_path)
            except pygame.error:
                self.crash_sound = None  # sound failed to load — continue silently

        # ── Sprite Groups ──
        # Separate groups allow targeted collision checks and bulk updates
        self.traffic     = pygame.sprite.Group()  # enemy cars
        self.coins_group = pygame.sprite.Group()  # collectible coins
        self.obstacles   = pygame.sprite.Group()  # road hazards
        self.powerups    = pygame.sprite.Group()  # power-up pickups
        self.road_events = pygame.sprite.Group()  # speed bumps, nitro strips, barriers
        self.all_sprites = pygame.sprite.Group(self.player)  # everything drawn together

        # ── Game State ──
        self.coins       = 0      # coins collected this run
        self.distance    = 0      # meters traveled (increases each frame)
        self.score       = 0      # distance + coins * 15
        self.active_power   = None  # currently active power-up name, or None
        self.power_end_time = 0     # ms timestamp when Nitro expires
        self.shield_ready   = False # True when Shield power-up is active
        self.slow_until     = 0     # ms timestamp until slow effect expires
        self.game_over      = False
        self.frame_count    = 0     # incremented every update(), used for spawn timing

        # Spawn intervals (in frames) — get shorter as distance increases
        self.traffic_delay  = self.config["traffic"]
        self.obstacle_delay = self.config["obstacle"]
        self.event_delay    = self.config["event"]
        self.power_delay    = 260   # power-up spawn interval (fixed)
        self.coin_delay     = 55    # coin spawn interval (fixed)

    # ── SPAWNING ──

    def spawn_traffic(self):
        """
        Spawn a traffic car and add it to both the traffic group and all_sprites.
        Speed scales up with distance (harder as the run progresses).
        Uses spritecollideany to avoid spawning on top of another car.
        """
        car = TrafficCar(self.base_speed + self.distance // 700, self.player.rect)
        if not pygame.sprite.spritecollideany(car, self.traffic):
            self.traffic.add(car)
            self.all_sprites.add(car)

    def spawn_obstacle(self):
        obstacle = Obstacle(random.choice(["barrier", "oil", "pothole"]), self.base_speed, self.player.rect)
        self.obstacles.add(obstacle)
        self.all_sprites.add(obstacle)

    def spawn_powerup(self):
        power = PowerUp(random.choice(["Nitro", "Shield", "Repair"]), self.player.rect)
        self.powerups.add(power)
        self.all_sprites.add(power)

    def spawn_coin(self):
        coin = Coin(self.player.rect)
        self.coins_group.add(coin)
        self.all_sprites.add(coin)

    def spawn_road_event(self):
        event = RoadEvent(random.choice(["speed_bump", "nitro_strip", "moving_barrier"]), self.base_speed, self.player.rect)
        self.road_events.add(event)
        self.all_sprites.add(event)

    # ── DIFFICULTY SCALING ──

    def apply_difficulty_scaling(self):
        """
        Reduce spawn intervals as the player travels further.
        level = one increment per 500m traveled.
        Each level shaves frames off the spawn delays, clamped at a minimum
        so the game doesn't become impossible.
        """
        level = self.distance // 500
        self.traffic_delay  = max(30,  self.config["traffic"]   - level * 8)
        self.obstacle_delay = max(45,  self.config["obstacle"]  - level * 8)
        self.event_delay    = max(100, self.config["event"]      - level * 10)

    # ── POWER-UPS ──

    def activate_power(self, kind):
        """
        Apply the effect of a collected power-up.
          Nitro:  sets active_power and records when it should expire (4 seconds)
          Shield: sets shield_ready flag — next dangerous collision is absorbed
          Repair: instantly kills the nearest hazard on the road
        """
        self.active_power = kind

        if kind == "Nitro":
            self.power_end_time = pygame.time.get_ticks() + 4000

        elif kind == "Shield":
            self.shield_ready   = True
            self.power_end_time = 0  # Shield doesn't time out — lasts until hit

        elif kind == "Repair":
            # Find the first available hazard to remove (priority: obstacle > traffic > event)
            target = None
            if len(self.obstacles)   > 0: target = list(self.obstacles)[0]
            elif len(self.traffic)   > 0: target = list(self.traffic)[0]
            elif len(self.road_events) > 0: target = list(self.road_events)[0]

            if target:
                target.kill()  # remove it from all groups

            self.active_power = None  # Repair is instant, no ongoing effect

    # ── COLLISION HANDLING ──

    def danger_hit(self, sprite=None):
        """
        Called when the player collides with something dangerous.
        If Shield is active: absorb the hit (kill the hazard, deactivate shield).
        Otherwise: play crash sound and set game_over = True.
        """
        if self.shield_ready:
            self.shield_ready = False
            self.active_power = None
            if sprite:
                sprite.kill()  # remove the hazard that was blocked
        else:
            if self.crash_sound:
                self.crash_sound.play()
            self.game_over = True

    def handle_collision_with_danger(self, group):
        """Check for collision between the player and any sprite in the group."""
        hit = pygame.sprite.spritecollideany(self.player, group)
        if hit:
            self.danger_hit(hit)

    # ── MAIN UPDATE ──

    def update(self):
        """
        Called every frame. Handles all game logic:
        - Difficulty scaling
        - Power-up expiry
        - Speed calculation (base + nitro bonus - slow penalty + distance scaling)
        - Distance and score tracking
        - Spawning objects on frame intervals
        - Updating all sprite groups
        - Collision detection (coins, power-ups, road events, obstacles, traffic)
        - Win condition check
        """
        self.frame_count += 1
        self.apply_difficulty_scaling()

        now = pygame.time.get_ticks()

        # Check if Nitro has expired
        if self.active_power == "Nitro" and now > self.power_end_time:
            self.active_power = None

        # Slow effect (from oil slick or speed bump)
        speed_penalty = 2 if now < self.slow_until else 0

        # Nitro adds +3 speed; distance naturally scales speed up over time
        speed_bonus   = 3 if self.active_power == "Nitro" else 0
        current_speed = max(2, self.base_speed + speed_bonus + self.distance // 900 - speed_penalty)

        # Distance grows proportional to current speed each frame
        self.distance += max(1, current_speed // 2)
        self.score     = self.distance + self.coins * 15  # coins are worth 15 points each

        # Spawn objects on fixed frame intervals
        if self.frame_count % self.traffic_delay  == 0: self.spawn_traffic()
        if self.frame_count % self.obstacle_delay == 0: self.spawn_obstacle()
        if self.frame_count % self.power_delay    == 0: self.spawn_powerup()
        if self.frame_count % self.coin_delay     == 0: self.spawn_coin()
        if self.frame_count % self.event_delay    == 0: self.spawn_road_event()

        # Update all sprites (calls each sprite's update() method)
        self.player.update()
        for group in [self.traffic, self.obstacles, self.coins_group, self.powerups, self.road_events]:
            group.update()

        # ── Collision: Coins ──
        # True = remove coin from group on contact
        for coin in pygame.sprite.spritecollide(self.player, self.coins_group, True):
            self.coins += coin.value

        # ── Collision: Power-ups ──
        # Only activate if no power-up is currently running
        for power in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if self.active_power is None:
                self.activate_power(power.kind)

        # ── Collision: Road Events ──
        for event in pygame.sprite.spritecollide(self.player, self.road_events, True):
            if event.type == "nitro_strip" and self.active_power is None:
                self.activate_power("Nitro")  # free Nitro from the road
            elif event.type == "speed_bump":
                self.slow_until = now + 1800   # slow for 1.8 seconds
            else:
                self.danger_hit(event)  # moving_barrier causes a crash

        # ── Collision: Obstacles ──
        for obstacle in pygame.sprite.spritecollide(self.player, self.obstacles, False):
            if obstacle.type == "oil":
                self.slow_until = now + 2000  # oil slows for 2 seconds
                obstacle.kill()                # remove oil after touching it
            else:
                self.danger_hit(obstacle)  # barrier/pothole cause crash

        # ── Collision: Traffic ──
        self.handle_collision_with_danger(self.traffic)

        # ── Win condition ──
        if self.distance >= FINISH_DISTANCE:
            self.game_over = True

    # ── DRAWING ──

    def draw_road(self):
        """
        Scroll the background image downward to simulate forward movement.
        We blit the image twice — once at bg_y and once at bg_y - HEIGHT —
        so there's always a seamless tile covering the full screen.
        bg_y wraps around using modulo HEIGHT so it never goes out of range.
        """
        self.bg_y = (self.bg_y + self.base_speed) % HEIGHT
        self.screen.blit(self.background, (0, self.bg_y))
        self.screen.blit(self.background, (0, self.bg_y - HEIGHT))

    def draw_hud(self):
        """
        Draw the heads-up display: score, coins, distance, remaining distance,
        active power-up status, and slow-zone warning.
        A semi-transparent black bar at the top provides a readable background.
        """
        remaining = max(0, FINISH_DISTANCE - self.distance)

        # Dark bar behind the HUD text for readability
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (0, 0, WIDTH, 96))

        draw_text(self.screen, f"Score: {self.score}",        16, WHITE,  8, 8)
        draw_text(self.screen, f"Coins: {self.coins}",        16, WHITE,  8, 30)
        draw_text(self.screen, f"Distance: {self.distance}m", 16, WHITE,  8, 52)
        draw_text(self.screen, f"Left: {remaining}m",         16, WHITE,  8, 74)

        # Active power-up display
        if self.active_power == "Nitro":
            left = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
            text = f"Power: Nitro {left}s"
        elif self.active_power == "Shield":
            text = "Power: Shield 1 hit"
        else:
            text = "Power: None"
        draw_text(self.screen, text, 16, YELLOW, 210, 8)

        # Slow zone warning
        if pygame.time.get_ticks() < self.slow_until:
            draw_text(self.screen, "Slow zone!", 16, ORANGE, 210, 32)

    def draw(self):
        """Draw everything: road → sprites → HUD (in that order so HUD is on top)."""
        self.draw_road()
        self.all_sprites.draw(self.screen)  # draws all sprites using their .image and .rect
        self.draw_hud()

    # ── GAME LOOP ──

    def run(self):
        """
        The main game loop. Runs at FPS (60) until game_over is True.
        Each iteration: handle events → update game state → draw → display.

        Returns:
            ("quit", None)         if the window was closed mid-game
            ("game_over", result)  when the game ends normally (crash or finish)
                                   result contains score, distance, coins, name
        """
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", None  # window closed — signal immediate exit

            self.update()  # advance all game logic by one frame
            self.draw()    # render everything to the screen
            pygame.display.update()
            self.clock.tick(FPS)  # cap at 60 FPS

        # ── Game ended — build result and save to leaderboard ──
        result = {
            "name":     self.username,
            "score":    self.score,
            "distance": self.distance,
            "coins":    self.coins,
        }
        add_score(self.username, self.score, self.distance, self.coins)
        return "game_over", result