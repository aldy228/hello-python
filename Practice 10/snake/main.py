"""
Main Game Module - Snake

This is the main entry point for the Snake game.
It handles:
- Game initialization and grid setup
- Main game loop
- Input processing (arrow keys)
- Collision detection and game over logic
- Level progression and speed scaling
- Score tracking and UI rendering
- Restart functionality

Game Objective: Eat food to grow. Avoid walls and yourself.
Level up every 4 foods to increase speed.
"""

import pygame  # Import pygame library
import sys  # Import sys for clean program exit
from snake import Snake  # Import Snake class
from food import Food  # Import Food class

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize all pygame modules
pygame.init()

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# INCREASED SCREEN SIZE for better visibility
SCREEN_WIDTH = 800   # Was 600
SCREEN_HEIGHT = 800  # Was 600
BLOCK_SIZE = 20      # Size of each grid cell (snake segments and food)
FPS = 10             # Starting frames per second (controls snake speed)

# Define colors using RGB values
WHITE = (255, 255, 255)  # Background color
BLACK = (0, 0, 0)        # Text and outline color
GREEN = (0, 200, 0)      # Snake color
RED = (255, 0, 0)        # Food color

# ============================================================================
# DISPLAY & FONT SETUP
# ============================================================================

# Create game window surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set window title
pygame.display.set_caption("Snake")

# Create clock to control frame rate
clock = pygame.time.Clock()

# Create font for UI text (None = default pygame font, 36 = size)
font = pygame.font.Font(None, 36)

# ============================================================================
# GAME OBJECTS
# ============================================================================

# Create snake instance
# Pass block size and screen dimensions for boundary checking
snake = Snake(BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

# Create food instance
# Pass snake.body so food can avoid spawning on the snake
food = Food(BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, snake.body)

# ============================================================================
# GAME STATE VARIABLES
# ============================================================================

score = 0        # Player's current score
level = 1        # Current game level
foods_eaten = 0  # Counter for foods eaten this level
game_over = False  # Tracks if game has ended

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def show_ui():
    """
    Display score and level in top corners of screen
    
    Uses font.render() to create text surfaces, then blits them to screen.
    """
    # Render score text
    score_text = font.render(f"Score: {score}", True, BLACK)
    # Draw at top-left (15, 15) for better margin on larger screen
    screen.blit(score_text, (15, 15))
    
    # Render level text
    level_text = font.render(f"Level: {level}", True, BLACK)
    # Draw at top-right (SCREEN_WIDTH - 150, 15)
    screen.blit(level_text, (SCREEN_WIDTH - 150, 15))

def show_game_over():
    """
    Display game over overlay with restart instructions
    
    Creates a semi-transparent white overlay, then draws centered text.
    """
    # Create overlay surface matching screen size
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Set alpha (transparency) to 200 out of 255 (mostly opaque)
    overlay.set_alpha(200)
    # Fill with white
    overlay.fill(WHITE)
    # Draw overlay on top of everything
    screen.blit(overlay, (0, 0))
    
    # Render "GAME OVER" text in red
    go_text = font.render("GAME OVER", True, RED)
    # Render restart instruction in black
    restart_text = font.render("Press R to Restart", True, BLACK)
    
    # Calculate center positions for text
    # SCREEN_WIDTH//2 - text_width//2 centers horizontally
    screen.blit(go_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 30))
    screen.blit(restart_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 10))

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

running = True  # Controls main loop execution

while running:
    """
    Main game loop - runs continuously until program exits
    
    Each frame:
    1. Process events (keyboard, window close)
    2. Update game logic (movement, collisions, levels)
    3. Render screen (background, snake, food, UI)
    4. Control frame rate
    """
    
    # -------------------------------------------------------------------------
    # EVENT HANDLING
    # -------------------------------------------------------------------------
    for event in pygame.event.get():
        # Check for window close button
        if event.type == pygame.QUIT:
            running = False
        
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Arrow keys control snake direction
            # Each direction is a vector: (x_change, y_change)
            if event.key == pygame.K_UP:
                snake.change_direction((0, -1))  # Up: y decreases
            elif event.key == pygame.K_DOWN:
                snake.change_direction((0, 1))   # Down: y increases
            elif event.key == pygame.K_LEFT:
                snake.change_direction((-1, 0))  # Left: x decreases
            elif event.key == pygame.K_RIGHT:
                snake.change_direction((1, 0))   # Right: x increases
            
            # Restart game if game over and R is pressed
            elif event.key == pygame.K_r and game_over:
                # Reset all game objects to initial state
                snake = Snake(BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
                food = Food(BLOCK_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, snake.body)
                
                # Reset game variables
                score = 0
                level = 1
                foods_eaten = 0
                FPS = 10  # Reset speed to starting value
                game_over = False
    
    # -------------------------------------------------------------------------
    # GAME LOGIC (only runs if game is not over)
    # -------------------------------------------------------------------------
    if not game_over:
        # Move snake one step
        snake.move()
        
        # Check for wall or self collision
        if snake.check_collision():
            # Set game over flag
            game_over = True
        
        # Check if snake head is at same position as food
        # Both are grid-aligned, so exact tuple comparison works
        if snake.get_head() == food.get_position():
            # Grow snake
            snake.grow()
            
            # Spawn new food at valid position
            food.respawn(snake.body)
            
            # Update score
            score += 10
            
            # Increment foods eaten counter
            foods_eaten += 1
            
            # Check for level up condition
            # Level up every 4 foods eaten
            if foods_eaten >= 4:
                level += 1  # Increase level
                foods_eaten = 0  # Reset counter
                FPS += 2  # Increase game speed (more frames per second)
        
        # -------------------------------------------------------------------------
        # RENDERING
        # -------------------------------------------------------------------------
        
        # Fill screen with background color
        screen.fill(WHITE)
        
        # Draw snake and food
        snake.draw(screen)
        food.draw(screen)
        
        # Draw UI (score, level)
        show_ui()
    else:
        # If game over, show overlay screen
        show_game_over()
    
    # -------------------------------------------------------------------------
    # DISPLAY UPDATE & FRAME CONTROL
    # -------------------------------------------------------------------------
    
    # Update display to show all drawn elements
    pygame.display.flip()
    
    # Control frame rate to maintain consistent speed
    # Higher FPS = faster snake movement
    clock.tick(FPS)

# ============================================================================
# CLEANUP
# ============================================================================

# Quit pygame and release resources
pygame.quit()

# Exit Python program
sys.exit()