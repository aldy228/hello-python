import pygame
import sys
import os
from clock import MickeysClock

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mickey's Clock")
clock = pygame.time.Clock()

# Get the directory where main.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "images", "mickey_hand.png")

# Create clock object
mickey_clock = MickeysClock(image_path)
mickey_clock.set_center(CENTER[0], CENTER[1])

def draw_clock_face():
    """Draw the clock circle and center dot"""
    # Draw clock face
    pygame.draw.circle(screen, BLACK, CENTER, 350, 5)
    
    # Draw center dot
    pygame.draw.circle(screen, BLACK, CENTER, 15)

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get rotated hands
    minute_hand, minute_rect = mickey_clock.get_minute_hand()
    second_hand, second_rect = mickey_clock.get_second_hand()
    
    # Drawing
    screen.fill(WHITE)
    draw_clock_face()
    
    # Draw hands (minute first, then second on top)
    screen.blit(minute_hand, minute_rect)
    screen.blit(second_hand, second_rect)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()