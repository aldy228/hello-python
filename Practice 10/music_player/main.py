import pygame
import sys
from player import MusicPlayer

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
FPS = 30

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Music Player")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Create music player
player = MusicPlayer("music/sample_tracks")

def draw_ui():
    """Draw the user interface"""
    screen.fill(WHITE)
    
    # Title
    title = font_large.render("MUSIC PLAYER", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
    
    # Controls
    controls_y = 150
    controls = [
        "Controls:",
        "P - Play",
        "S - Stop",
        "N - Next Track",
        "B - Previous Track",
        "Q - Quit"
    ]
    
    for i, text in enumerate(controls):
        if i == 0:
            text_surface = font_medium.render(text, True, BLACK)
        else:
            text_surface = font_small.render(text, True, GRAY)
        screen.blit(text_surface, (50, controls_y + i * 40))
    
    # Track info
    info_y = 450
    if player.get_track_count() > 0:
        track_info = font_medium.render(
            f"Track: {player.get_current_index()}/{player.get_track_count()}",
            True, BLACK
        )
        screen.blit(track_info, (50, info_y))
        
        track_name = font_small.render(
            f"File: {player.get_current_name()}",
            True, BLACK
        )
        screen.blit(track_name, (50, info_y + 40))
        
        # Position
        position = player.get_position()
        pos_text = font_small.render(f"Position: {position:.1f}s", True, GRAY)
        screen.blit(pos_text, (50, info_y + 70))
    else:
        no_tracks = font_medium.render(
            "No tracks found in music/ folder",
            True, (255, 0, 0)
        )
        screen.blit(no_tracks, (50, info_y))

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Play
                player.play()
            elif event.key == pygame.K_s:  # Stop
                player.stop()
            elif event.key == pygame.K_n:  # Next
                player.next_track()
            elif event.key == pygame.K_b:  # Previous/Back
                player.prev_track()
            elif event.key == pygame.K_q:  # Quit
                running = False
    
    # Draw everything
    draw_ui()
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit()