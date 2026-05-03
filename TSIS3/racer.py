import os
import random
import pygame
from persistence import add_score

WIDTH = 400
HEIGHT = 600
FPS = 60
FINISH_DISTANCE = 3000

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (120, 120, 120)
RED = (220, 50, 50)
BLUE = (40, 160, 255)
GREEN = (60, 180, 80)
YELLOW = (245, 210, 60)
ORANGE = (245, 130, 40)
PURPLE = (150, 80, 220)
CYAN = (60, 220, 220)
BROWN = (70, 45, 35)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

ROAD_LEFT = 40
ROAD_RIGHT = 360
LANES = [95, 200, 305]

CAR_IMAGES = {
    "Orange": "Player_orange.png",
    "Blue": "Player_blue.png",
    "Yellow": "Player_yellow.png",
    "Green": "Player_green.png",
    "Purple": "Player_purple.png",
}

DIFFICULTY = {
    "Easy": {"speed": 4, "traffic": 120, "obstacle": 170, "event": 320},
    "Normal": {"speed": 5, "traffic": 90, "obstacle": 130, "event": 260},
    "Hard": {"speed": 6, "traffic": 65, "obstacle": 100, "event": 210},
}


def draw_text(surface, text, size, color, x, y, center=False):
    font = pygame.font.SysFont("Verdana", size)
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(image, rect)


def load_image(filename, size=None):
    path = os.path.join(ASSET_DIR, filename)
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image


def load_player_car(color_name):
    """Load the exact car image chosen in Settings.
    1 = Orange, 2 = Blue, 3 = Yellow, 4 = Green, 5 = Purple.
    """
    filename = CAR_IMAGES.get(color_name, CAR_IMAGES["Orange"])
    return load_image(filename, (44, 96))


def safe_spawn_y(player_rect):
    """New objects spawn above the screen, not directly on the player."""
    if player_rect.top < 160:
        return random.randint(-360, -100)
    return random.randint(-520, -120)


class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        self.image = load_player_car(color_name)
        self.rect = self.image.get_rect(center=(200, 500))
        self.speed = 6

    def update(self):
        keys = pygame.key.get_pressed()

        # The player can only change lanes left/right.
        # UP and DOWN are intentionally ignored during gameplay.
        if keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.x += self.speed


class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, speed, player_rect):
        super().__init__()
        self.image = load_image("Enemy.png", (48, 93))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = safe_spawn_y(player_rect)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.value = random.choice([1, 2, 3])
        size = 16 + self.value * 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, ORANGE, (size // 2, size // 2), size // 2, 3)
        font = pygame.font.SysFont("Verdana", 12, bold=True)
        txt = font.render(str(self.value), True, BLACK)
        self.image.blit(txt, txt.get_rect(center=(size // 2, size // 2)))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = safe_spawn_y(player_rect)
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type, speed, player_rect):
        super().__init__()
        self.type = obstacle_type
        self.speed = speed

        if self.type == "barrier":
            self.image = pygame.Surface((75, 25), pygame.SRCALPHA)
            pygame.draw.rect(self.image, ORANGE, (0, 0, 75, 25), border_radius=4)
            pygame.draw.line(self.image, WHITE, (6, 20), (68, 4), 4)
        elif self.type == "oil":
            self.image = pygame.Surface((55, 35), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, BLACK, (0, 0, 55, 35))
            pygame.draw.ellipse(self.image, (70, 70, 70), (12, 8, 25, 12))
        else:  # pothole
            self.image = pygame.Surface((50, 34), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, BROWN, (0, 0, 50, 34))
            pygame.draw.ellipse(self.image, BLACK, (9, 8, 30, 15))

        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = safe_spawn_y(player_rect)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, player_rect):
        super().__init__()
        self.kind = kind
        self.spawn_time = pygame.time.get_ticks()
        self.timeout = 6000
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)

        if kind == "Nitro":
            color, letter = CYAN, "N"
        elif kind == "Shield":
            color, letter = PURPLE, "S"
        else:
            color, letter = GREEN, "R"

        pygame.draw.circle(self.image, color, (18, 18), 18)
        pygame.draw.circle(self.image, WHITE, (18, 18), 18, 2)
        font = pygame.font.SysFont("Verdana", 19, bold=True)
        text = font.render(letter, True, WHITE)
        self.image.blit(text, text.get_rect(center=(18, 17)))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = safe_spawn_y(player_rect)
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
        if pygame.time.get_ticks() - self.spawn_time > self.timeout:
            self.kill()


class RoadEvent(pygame.sprite.Sprite):
    def __init__(self, event_type, speed, player_rect):
        super().__init__()
        self.type = event_type
        self.speed = speed

        if event_type == "speed_bump":
            self.image = pygame.Surface((90, 20), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (0, 0, 90, 20), border_radius=6)
            pygame.draw.line(self.image, BLACK, (10, 5), (80, 5), 3)
            pygame.draw.line(self.image, BLACK, (10, 15), (80, 15), 3)
        elif event_type == "nitro_strip":
            self.image = pygame.Surface((75, 28), pygame.SRCALPHA)
            pygame.draw.rect(self.image, CYAN, (0, 0, 75, 28), border_radius=8)
            pygame.draw.polygon(self.image, WHITE, [(10, 22), (25, 6), (25, 16), (45, 6), (31, 22)])
        else:  # moving barrier
            self.image = pygame.Surface((75, 25), pygame.SRCALPHA)
            pygame.draw.rect(self.image, ORANGE, (0, 0, 75, 25), border_radius=4)
            pygame.draw.line(self.image, WHITE, (6, 20), (68, 4), 4)

        self.rect = self.image.get_rect()
        self.rect.centerx = random.choice(LANES)
        self.rect.y = safe_spawn_y(player_rect)
        self.direction = random.choice([-2, 2])

    def update(self):
        self.rect.y += self.speed
        if self.type == "moving_barrier":
            self.rect.x += self.direction
            if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
                self.direction *= -1
        if self.rect.top > HEIGHT:
            self.kill()


class RacerGame:
    def __init__(self, screen, clock, settings, username):
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.username = username
        self.config = DIFFICULTY[settings["difficulty"]]
        self.base_speed = self.config["speed"]
        self.background = load_image("AnimatedStreet.png", (WIDTH, HEIGHT))
        self.bg_y = 0
        self.player = Player(settings["car_color"])

        self.crash_sound = None
        crash_path = os.path.join(ASSET_DIR, "crash.wav")
        if settings.get("sound", True) and os.path.exists(crash_path):
            try:
                self.crash_sound = pygame.mixer.Sound(crash_path)
            except pygame.error:
                self.crash_sound = None

        self.traffic = pygame.sprite.Group()
        self.coins_group = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.road_events = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)

        self.coins = 0
        self.distance = 0
        self.score = 0
        self.active_power = None
        self.power_end_time = 0
        self.shield_ready = False
        self.slow_until = 0
        self.game_over = False
        self.frame_count = 0
        self.traffic_delay = self.config["traffic"]
        self.obstacle_delay = self.config["obstacle"]
        self.event_delay = self.config["event"]
        self.power_delay = 260
        self.coin_delay = 55

    def spawn_traffic(self):
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

    def apply_difficulty_scaling(self):
        level = self.distance // 500
        self.traffic_delay = max(30, self.config["traffic"] - level * 8)
        self.obstacle_delay = max(45, self.config["obstacle"] - level * 8)
        self.event_delay = max(100, self.config["event"] - level * 10)

    def activate_power(self, kind):
        self.active_power = kind
        if kind == "Nitro":
            self.power_end_time = pygame.time.get_ticks() + 4000
        elif kind == "Shield":
            self.shield_ready = True
            self.power_end_time = 0
        elif kind == "Repair":
            # Instant repair: remove one danger from the road.
            target = None
            if len(self.obstacles) > 0:
                target = list(self.obstacles)[0]
            elif len(self.traffic) > 0:
                target = list(self.traffic)[0]
            elif len(self.road_events) > 0:
                target = list(self.road_events)[0]
            if target:
                target.kill()
            self.active_power = None

    def danger_hit(self, sprite=None):
        if self.shield_ready:
            self.shield_ready = False
            self.active_power = None
            if sprite:
                sprite.kill()
        else:
            if self.crash_sound:
                self.crash_sound.play()
            self.game_over = True

    def handle_collision_with_danger(self, group):
        hit = pygame.sprite.spritecollideany(self.player, group)
        if hit:
            self.danger_hit(hit)

    def update(self):
        self.frame_count += 1
        self.apply_difficulty_scaling()

        now = pygame.time.get_ticks()
        if self.active_power == "Nitro" and now > self.power_end_time:
            self.active_power = None
        if now < self.slow_until:
            speed_penalty = 2
        else:
            speed_penalty = 0

        speed_bonus = 3 if self.active_power == "Nitro" else 0
        current_speed = max(2, self.base_speed + speed_bonus + self.distance // 900 - speed_penalty)
        self.distance += max(1, current_speed // 2)
        self.score = self.distance + self.coins * 15

        if self.frame_count % self.traffic_delay == 0:
            self.spawn_traffic()
        if self.frame_count % self.obstacle_delay == 0:
            self.spawn_obstacle()
        if self.frame_count % self.power_delay == 0:
            self.spawn_powerup()
        if self.frame_count % self.coin_delay == 0:
            self.spawn_coin()
        if self.frame_count % self.event_delay == 0:
            self.spawn_road_event()

        self.player.update()
        for group in [self.traffic, self.obstacles, self.coins_group, self.powerups, self.road_events]:
            group.update()

        for coin in pygame.sprite.spritecollide(self.player, self.coins_group, True):
            self.coins += coin.value

        for power in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if self.active_power is None:
                self.activate_power(power.kind)

        for event in pygame.sprite.spritecollide(self.player, self.road_events, True):
            if event.type == "nitro_strip" and self.active_power is None:
                self.activate_power("Nitro")
            elif event.type == "speed_bump":
                self.slow_until = now + 1800
            else:
                self.danger_hit(event)

        for obstacle in pygame.sprite.spritecollide(self.player, self.obstacles, False):
            if obstacle.type == "oil":
                self.slow_until = now + 2000
                obstacle.kill()
            else:
                self.danger_hit(obstacle)

        self.handle_collision_with_danger(self.traffic)

        if self.distance >= FINISH_DISTANCE:
            self.game_over = True

    def draw_road(self):
        self.bg_y = (self.bg_y + self.base_speed) % HEIGHT
        self.screen.blit(self.background, (0, self.bg_y))
        self.screen.blit(self.background, (0, self.bg_y - HEIGHT))

    def draw_hud(self):
        remaining = max(0, FINISH_DISTANCE - self.distance)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (0, 0, WIDTH, 96))
        draw_text(self.screen, f"Score: {self.score}", 16, WHITE, 8, 8)
        draw_text(self.screen, f"Coins: {self.coins}", 16, WHITE, 8, 30)
        draw_text(self.screen, f"Distance: {self.distance}m", 16, WHITE, 8, 52)
        draw_text(self.screen, f"Left: {remaining}m", 16, WHITE, 8, 74)

        if self.active_power == "Nitro":
            left = max(0, (self.power_end_time - pygame.time.get_ticks()) // 1000)
            text = f"Power: Nitro {left}s"
        elif self.active_power == "Shield":
            text = "Power: Shield 1 hit"
        else:
            text = "Power: None"
        draw_text(self.screen, text, 16, YELLOW, 210, 8)

        if pygame.time.get_ticks() < self.slow_until:
            draw_text(self.screen, "Slow zone!", 16, ORANGE, 210, 32)

    def draw(self):
        self.draw_road()
        self.all_sprites.draw(self.screen)
        self.draw_hud()

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", None

            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)

        result = {
            "name": self.username,
            "score": self.score,
            "distance": self.distance,
            "coins": self.coins,
        }
        add_score(self.username, self.score, self.distance, self.coins)
        return "game_over", result