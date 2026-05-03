"""
Main Game Module - Racer (Final Enhanced Version)

Changes:
1. Score increases slower (every 10 frames instead of every frame)
2. Coins give points based on their type (gold=10, silver=5, bronze=3)
3. Road barriers added to constrain player movement
4. Coins move faster as level increases
"""

import pygame
import sys
import random
import os
from player import Player
from enemy import Enemy
from coin import Coin

# ============================================================================
# INITIALIZATION
# ============================================================================

pygame.init()

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
ROAD_WIDTH = 500
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)  # For barriers
GREEN = (0, 200, 0)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Game balance constants
COINS_FOR_SPEED_INCREASE = 5
SPEED_INCREMENT = 1
SCORE_INTERVAL = 10  # Add 1 point every N frames (was 1)

# ============================================================================
# DISPLAY SETUP
# ============================================================================

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

# ============================================================================
# SPRITE GROUPS
# ============================================================================

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()

# ============================================================================
# GAME OBJECT CREATION
# ============================================================================

script_dir = os.path.dirname(os.path.abspath(__file__))
images_dir = os.path.join(script_dir, "images")

player_image = os.path.join(images_dir, "player_car.png")
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, image_path=player_image)
all_sprites.add(player)

# ============================================================================
# GAME STATE VARIABLES
# ============================================================================

score = 0
coin_count = 0
level = 1
enemy_timer = 0
coin_timer = 0
frame_counter = 0  # For slower score increase
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
game_over = False
base_enemy_speed = 3
base_coin_speed = 4  # Base speed for coins

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def draw_road():
    """
    Draw the road with barriers on both sides
    
    Now includes:
    1. Green grass background
    2. Dark gray barriers on road edges
    3. Gray road surface
    4. White lane markers
    """
    # Fill screen with green grass
    screen.fill(GREEN)
    
    # Calculate road position
    road_x = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    
    # === NEW: Draw barriers on both sides of road ===
    barrier_width = 20
    # Left barrier
    pygame.draw.rect(screen, DARK_GRAY, 
                    (road_x - barrier_width, 0, barrier_width, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BLACK, 
                    (road_x - barrier_width, 0, barrier_width, SCREEN_HEIGHT), 2)
    # Right barrier
    pygame.draw.rect(screen, DARK_GRAY, 
                    (road_x + ROAD_WIDTH, 0, barrier_width, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BLACK, 
                    (road_x + ROAD_WIDTH, 0, barrier_width, SCREEN_HEIGHT), 2)
    
    # Draw the road as a gray rectangle
    pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    
    # Draw dashed white lane markers
    for y in range(-50, SCREEN_HEIGHT, 100):
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 5, y, 10, 50))

def spawn_enemy():
    """Create enemy car constrained to road"""
    road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    road_right = road_left + ROAD_WIDTH
    
    enemy = Enemy(SCREEN_WIDTH, road_left + 60, road_right - 60, 
                  base_enemy_speed, 
                  image_path=os.path.join(images_dir, "enemy_car.png"))
    enemies.add(enemy)
    all_sprites.add(enemy)

def spawn_coin():
    """Create coin constrained to road with level-based speed"""
    road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    road_right = road_left + ROAD_WIDTH
    
    # NEW: Pass coin_speed that increases with level
    coin_speed = base_coin_speed + (level - 1) * 0.5
    
    coin = Coin(SCREEN_WIDTH, road_left + 60, road_right - 60, 
                coin_speed=coin_speed,
                image_path=os.path.join(images_dir, "coin.png"))
    coins.add(coin)
    all_sprites.add(coin)

def show_ui():
    """Display score, coins, and level"""
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    coin_text = font.render(f"Coins: {coin_count}", True, YELLOW)
    screen.blit(coin_text, (SCREEN_WIDTH - 200, 20))
    
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH - 200, 70))

def show_game_over():
    """Display game over overlay"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    
    title = font.render("GAME OVER", True, RED)
    screen.blit(title, (center_x - title.get_width()//2, center_y - 100))
    
    final_score = small_font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(final_score, (center_x - final_score.get_width()//2, center_y - 20))
    
    final_level = small_font.render(f"Level Reached: {level}", True, WHITE)
    screen.blit(final_level, (center_x - final_level.get_width()//2, center_y + 30))
    
    final_coins = small_font.render(f"Coins Collected: {coin_count}", True, YELLOW)
    screen.blit(final_coins, (center_x - final_coins.get_width()//2, center_y + 80))
    
    restart_text = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(restart_text, (center_x - restart_text.get_width()//2, center_y + 150))

def reset_game():
    """Reset all game variables"""
    global score, coin_count, level, enemy_timer, coin_timer, game_over
    global base_enemy_speed, base_coin_speed, frame_counter
    
    score = 0
    coin_count = 0
    level = 1
    enemy_timer = 0
    coin_timer = 0
    frame_counter = 0
    game_over = False
    base_enemy_speed = 3
    base_coin_speed = 4
    
    all_sprites.empty()
    enemies.empty()
    coins.empty()
    
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    all_sprites.add(player)

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_q:
                running = False
    
    if not game_over:
        # Input handling
        keys = pygame.key.get_pressed()
        
        # === UPDATED: Player movement constrained to road ===
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = road_left + ROAD_WIDTH
        
        # Move left: check road boundary instead of screen edge
        if keys[pygame.K_LEFT] and player.rect.left > road_left + 5:
            player.rect.x -= player.speed
        
        # Move right: check road boundary instead of screen edge
        if keys[pygame.K_RIGHT] and player.rect.right < road_right - 5:
            player.rect.x += player.speed
        
        # Spawn enemies
        enemy_timer += 1
        if enemy_timer >= 60:
            spawn_enemy()
            enemy_timer = 0
        
        # Spawn coins
        coin_timer += 1
        if coin_timer >= 120:
            spawn_coin()
            coin_timer = 0
        
        # Update sprites
        enemies.update()
        coins.update()
        
        # Collision: player vs enemies
        if pygame.sprite.spritecollideany(player, enemies):
            game_over = True
        
        # Collision: player vs coins
        collected = pygame.sprite.spritecollide(player, coins, True)
        for coin in collected:
            # === UPDATED: Add coin's value to score (not just +10) ===
            score += coin.value  # gold=10, silver=5, bronze=3
            coin_count += 1
            
            # Increase enemy speed every N coins
            if coin_count % COINS_FOR_SPEED_INCREASE == 0:
                base_enemy_speed += SPEED_INCREMENT
                for enemy in enemies:
                    enemy.speed = base_enemy_speed
        
        # === UPDATED: Score increases slower (every SCORE_INTERVAL frames) ===
        frame_counter += 1
        if frame_counter >= SCORE_INTERVAL:
            score += 1  # Only add 1 point every 10 frames
            frame_counter = 0
        
        # Level up every 100 points
        if score >= level * 100:
            level += 1
            # Increase speeds for both enemies AND coins
            for enemy in enemies:
                enemy.speed += 1
            # Note: coin speed is set when spawning, so new coins will be faster
        
        # Rendering
        draw_road()
        all_sprites.draw(screen)
        show_ui()
    else:
        show_game_over()
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()