import pygame
import sys
from ball import Ball

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
FPS = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moving Ball Game")
clock = pygame.time.Clock()

# Create ball at center
ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get keyboard input
    keys = pygame.key.get_pressed()
    
    # Move ball with arrow keys
    if keys[pygame.K_UP]:
        ball.move_up(SCREEN_HEIGHT)
    
    if keys[pygame.K_DOWN]:
        ball.move_down(SCREEN_HEIGHT)
    
    if keys[pygame.K_LEFT]:
        ball.move_left(SCREEN_WIDTH)
    
    if keys[pygame.K_RIGHT]:
        ball.move_right(SCREEN_WIDTH)
    
    # Drawing
    screen.fill(WHITE)
    ball.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()