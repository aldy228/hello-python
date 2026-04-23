"""
Main Game Module - Racer

This is the main entry point for the Racer game.
It handles:
- Game initialization and setup
- Main game loop
- Spawning enemies and coins (constrained to road area)
- Collision detection
- Score and level management
- Rendering the game screen
- Game over screen with restart option

Game Objective: Avoid enemy cars and collect coins for points.
Level up every 100 points to increase difficulty.
"""

import pygame  # Import pygame library for game development
import sys  # Import sys for system functions (exiting the game)
import random  # Import random for random spawning
from player import Player  # Import Player class from player module
from enemy import Enemy  # Import Enemy class from enemy module
from coin import Coin  # Import Coin class from coin module

# ============================================================================
# INITIALIZATION SECTION
# ============================================================================

# Initialize all pygame modules (display, font, mixer, etc.)
# This must be called before using any pygame functions
pygame.init()

# ============================================================================
# CONSTANTS SECTION
# Define game configuration values that won't change during gameplay
# ============================================================================

# INCREASED SCREEN SIZE for better gameplay
SCREEN_WIDTH = 1000  # Was 800, now larger
SCREEN_HEIGHT = 800  # Was 700, now larger
ROAD_WIDTH = 500     # Wider road to match bigger screen
FPS = 60  # Frames Per Second - target frame rate for smooth animation

# Define colors using RGB (Red, Green, Blue) tuples
# Each value ranges from 0-255
WHITE = (255, 255, 255)  # Pure white (all colors max)
GRAY = (100, 100, 100)  # Medium gray for road
GREEN = (0, 200, 0)  # Bright green for grass/shoulders
YELLOW = (255, 215, 0)  # Gold/yellow for coins
RED = (255, 0, 0)  # Red for game over text
BLACK = (0, 0, 0)  # Black for outlines

# ============================================================================
# DISPLAY SETUP
# ============================================================================

# Create the main display surface (the game window)
# set_mode((width, height)) returns a Surface object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set the window title that appears in the title bar
pygame.display.set_caption("Racer")

# Create a Clock object to control frame rate
# This helps maintain consistent game speed across different computers
clock = pygame.time.Clock()

# ============================================================================
# SPRITE GROUPS
# Sprite groups help manage multiple game objects efficiently
# ============================================================================

# Group containing ALL sprites (player, enemies, coins)
# Used to update and draw all objects at once
all_sprites = pygame.sprite.Group()

# Group containing only enemy sprites
# Used for collision detection with player
enemies = pygame.sprite.Group()

# Group containing only coin sprites
# Used for collision detection (collection) by player
coins = pygame.sprite.Group()

# ============================================================================
# GAME OBJECT CREATION
# ============================================================================

# Create the player object
# Position: Horizontally centered (SCREEN_WIDTH // 2), near bottom (SCREEN_HEIGHT - 100)
# // is integer division (divides and rounds down)
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

# Add player to the all_sprites group so it gets updated and drawn
all_sprites.add(player)

# ============================================================================
# GAME STATE VARIABLES
# Track game progress and statistics
# ============================================================================

score = 0  # Total points accumulated during gameplay
coin_count = 0  # Number of coins collected (displayed in top-right)
level = 1  # Current level (increases difficulty)
enemy_timer = 0  # Counter to track when to spawn next enemy
coin_timer = 0  # Counter to track when to spawn next coin
font = pygame.font.Font(None, 48)  # Font for displaying text (larger for bigger screen)
small_font = pygame.font.Font(None, 36)  # Smaller font for secondary text
game_over = False  # Boolean flag to track if game has ended

# ============================================================================
# HELPER FUNCTIONS
# Functions to organize code and avoid repetition
# ============================================================================

def draw_road():
    """
    Draw the road and environment
    
    This function renders:
    1. Green grass background (full screen)
    2. Gray road in the center
    3. White lane markers (dashed lines)
    """
    # Fill entire screen with green color (grass)
    # This clears the previous frame
    screen.fill(GREEN)
    
    # Calculate road starting x-position to center it
    # (SCREEN_WIDTH - ROAD_WIDTH) // 2 gives equal margin on both sides
    road_x = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    
    # Draw the road as a gray rectangle
    # Parameters: surface, color, (x, y, width, height)
    # Road starts at road_x, top of screen (y=0), full height
    pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    
    # Draw dashed white lane markers in the center of the road
    # Loop from -50 to SCREEN_HEIGHT in steps of 100
    # Starting at -50 creates seamless scrolling effect
    for y in range(-50, SCREEN_HEIGHT, 100):
        # Draw each dash: 10 pixels wide, 50 pixels tall
        # Positioned at horizontal center (SCREEN_WIDTH//2 - 5)
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 5, y, 10, 50))

def spawn_enemy():
    """
    Create and add a new enemy car to the game
    
    FIXED: Enemies now spawn ONLY on the road, not on grass
    Calculates road boundaries and passes them to Enemy constructor.
    """
    # Calculate road boundaries
    road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    road_right = road_left + ROAD_WIDTH
    
    # Spawn enemy at random x-position WITHIN the road
    # Add padding (60px) so enemies don't spawn on the edges
    enemy = Enemy(SCREEN_WIDTH, road_left + 60, road_right - 60)
    enemies.add(enemy)
    all_sprites.add(enemy)

def spawn_coin():
    """
    Create and add a new collectible coin to the game
    
    FIXED: Coins also spawn only on the road
    """
    road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
    road_right = road_left + ROAD_WIDTH
    
    coin = Coin(SCREEN_WIDTH, road_left + 60, road_right - 60)
    coins.add(coin)
    all_sprites.add(coin)

def show_ui():
    """
    Display user interface elements on screen
    
    Renders and draws:
    1. Score (top-left)
    2. Coin count (top-right, in yellow)
    3. Current level (top-right, below coins)
    """
    # Render score text: "Score: X"
    # font.render(text, antialias, color) creates a Surface with text
    # antialias=True makes text smoother (but we use False for performance)
    score_text = font.render(f"Score: {score}", True, WHITE)
    
    # Draw score at position (20, 20) - top-left corner with 20px margin
    screen.blit(score_text, (20, 20))
    
    # Render coin count text in yellow color
    coin_text = font.render(f"Coins: {coin_count}", True, YELLOW)
    
    # Draw coin count at top-right corner
    # SCREEN_WIDTH - 200 positions it 200 pixels from right edge
    screen.blit(coin_text, (SCREEN_WIDTH - 200, 20))
    
    # Render level text
    level_text = font.render(f"Level: {level}", True, WHITE)
    
    # Draw level below coin count (y = 70)
    screen.blit(level_text, (SCREEN_WIDTH - 200, 70))

def show_game_over():
    """
    Display game over overlay with final score and restart option
    
    Creates a semi-transparent dark overlay, then draws:
    - "GAME OVER" title
    - Final score and level
    - Restart instructions
    """
    # Create dark semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)  # 200/255 transparency (mostly opaque)
    overlay.fill((0, 0, 0))  # Black background
    screen.blit(overlay, (0, 0))
    
    # Calculate center positions for text
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    
    # "GAME OVER" title in red
    title = font.render("GAME OVER", True, RED)
    screen.blit(title, (center_x - title.get_width()//2, center_y - 100))
    
    # Final score in white
    final_score = small_font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(final_score, (center_x - final_score.get_width()//2, center_y - 20))
    
    # Final level
    final_level = small_font.render(f"Level Reached: {level}", True, WHITE)
    screen.blit(final_level, (center_x - final_level.get_width()//2, center_y + 30))
    
    # Coins collected
    final_coins = small_font.render(f"Coins Collected: {coin_count}", True, YELLOW)
    screen.blit(final_coins, (center_x - final_coins.get_width()//2, center_y + 80))
    
    # Restart instruction
    restart_text = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(restart_text, (center_x - restart_text.get_width()//2, center_y + 150))

def reset_game():
    """
    Reset all game variables and objects to initial state
    
    Called when player presses R after game over.
    Clears all sprites and resets counters.
    """
    global score, coin_count, level, enemy_timer, coin_timer, game_over
    
    # Reset score and level
    score = 0
    coin_count = 0
    level = 1
    
    # Reset timers
    enemy_timer = 0
    coin_timer = 0
    
    # Reset game over flag
    game_over = False
    
    # Clear all sprite groups
    all_sprites.empty()
    enemies.empty()
    coins.empty()
    
    # Recreate player at starting position
    player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    all_sprites.add(player)

# ============================================================================
# MAIN GAME LOOP
# This is the heart of the game - runs continuously until game over
# ============================================================================

running = True  # Boolean flag to control game loop

while running:
    """
    Main game loop - executes once per frame (60 times per second)
    
    Each iteration performs:
    1. Event handling (quit, key presses)
    2. Update game objects (movement, spawning)
    3. Check collisions
    4. Update game state (score, level)
    5. Render everything to screen
    """
    
    # -------------------------------------------------------------------------
    # EVENT HANDLING
    # Process all pending events (user input, window events)
    # -------------------------------------------------------------------------
    for event in pygame.event.get():
        # Check if user clicked the window close button (X)
        if event.type == pygame.QUIT:
            # Set running to False to exit the game loop
            running = False
        
        # Handle key presses for game over screen
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Restart game
                reset_game()
            elif event.key == pygame.K_q:
                # Quit game
                running = False
    
    if not game_over:
        # ---------------------------------------------------------------------
        # INPUT HANDLING
        # Get current state of all keyboard keys
        # ---------------------------------------------------------------------
        keys = pygame.key.get_pressed()
        # Returns a dictionary-like object where keys[key_code] is True if pressed
        
        # ---------------------------------------------------------------------
        # UPDATE GAME OBJECTS
        # ---------------------------------------------------------------------
        
        # Update player position based on keyboard input
        # Pass keys dictionary and screen width for boundary checking
        player.update(keys, SCREEN_WIDTH)
        
        # ---------------------------------------------------------------------
        # ENEMY SPAWNING SYSTEM
        # ---------------------------------------------------------------------
        
        # Increment enemy timer each frame
        enemy_timer += 1
        
        # Check if enough frames have passed to spawn a new enemy
        # At 60 FPS, 60 frames = approximately 1 second
        if enemy_timer >= 60:
            # Call spawn function to create new enemy
            spawn_enemy()
            # Reset timer to 0 to start counting for next enemy
            enemy_timer = 0
        
        # ---------------------------------------------------------------------
        # COIN SPAWNING SYSTEM
        # ---------------------------------------------------------------------
        
        # Increment coin timer each frame
        coin_timer += 1
        
        # Spawn coins less frequently than enemies (every 120 frames = 2 seconds)
        # This makes coins more valuable and less common
        if coin_timer >= 120:
            spawn_coin()
            coin_timer = 0
        
        # ---------------------------------------------------------------------
        # UPDATE ALL SPRITES
        # ---------------------------------------------------------------------
        
        # Update all enemy positions (move them down the screen)
        # This calls the update() method on each enemy in the group
        enemies.update()
        
        # Update all coin positions (move them down the screen)
        coins.update()
        
        # ---------------------------------------------------------------------
        # COLLISION DETECTION
        # Check for interactions between game objects
        # ---------------------------------------------------------------------
        
        # Check if player collides with ANY enemy
        # spritecollideany(sprite, group) returns True if sprite overlaps any in group
        if pygame.sprite.spritecollideany(player, enemies):
            # Game over condition - player hit an enemy
            game_over = True  # Set game over flag instead of exiting immediately
        
        # Check if player collects any coins
        # spritecollide(sprite, group, dokill) returns list of collided sprites
        # dokill=True removes collected coins from the group automatically
        collected = pygame.sprite.spritecollide(player, coins, True)
        
        # Process each collected coin (usually just one per frame)
        for coin in collected:
            # Increment coin counter (displayed in UI)
            coin_count += 1
            # Add 10 points to score for collecting coin
            score += 10
        
        # ---------------------------------------------------------------------
        # SCORE AND LEVEL MANAGEMENT
        # ---------------------------------------------------------------------
        
        # Increase score by 1 every frame (survival points)
        # This rewards players for staying alive longer
        score += 1
        
        # Check if player has reached next level threshold
        # Level up every 100 points (100, 200, 300, etc.)
        if score >= level * 100:
            # Increase level
            level += 1
            
            # Increase difficulty by making all existing enemies faster
            # Loop through each enemy in the enemies group
            for enemy in enemies:
                # Increase enemy speed by 1 pixel per frame
                # This makes the game progressively harder
                enemy.speed += 1
        
        # ---------------------------------------------------------------------
        # RENDERING / DRAWING
        # Draw all game objects to the screen
        # ---------------------------------------------------------------------
        
        # Draw the road and environment (clears previous frame)
        draw_road()
        
        # Draw all sprites (player, enemies, coins)
        # This calls the draw() method which blits each sprite's image to screen
        all_sprites.draw(screen)
        
        # Draw user interface elements (score, coins, level)
        # Drawn last so they appear on top of everything
        show_ui()
    else:
        # Show game over screen overlay
        show_game_over()
    
    # -------------------------------------------------------------------------
    # DISPLAY UPDATE
    # -------------------------------------------------------------------------
    
    # Update the full display Surface to the screen
    # This swaps the back buffer (where we drew) with the front buffer (visible)
    pygame.display.flip()
    
    # Control frame rate - wait to maintain 60 FPS
    # tick(FPS) calculates how long to wait based on how long the frame took
    clock.tick(FPS)

# ============================================================================
# CLEANUP
# Game loop ended - clean up resources
# ============================================================================

# Quit pygame and clean up all resources
# This closes the window and frees memory
pygame.quit()

# Exit the Python program
sys.exit()