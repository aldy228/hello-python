import pygame
import sys
import os
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # (400, 400)
CLOCK_RADIUS = 350
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (253, 245, 230)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mickey's Clock")
clock = pygame.time.Clock()

# 1. Load Images
script_dir = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(script_dir, "images")

# Load Right Hand (Minutes)
try:
    right_hand_img = pygame.image.load(os.path.join(images_folder, "right_hand.png")).convert_alpha()
    right_hand_img = pygame.transform.scale(right_hand_img, (100, 200)) # Scale to fit
except:
    print("⚠️ right_hand.png not found, using fallback.")
    right_hand_img = pygame.Surface((100, 200), pygame.SRCALPHA)
    pygame.draw.rect(right_hand_img, WHITE, (0,0,100,200))

# Load Left Hand (Seconds)
try:
    left_hand_img = pygame.image.load(os.path.join(images_folder, "left_hand.png")).convert_alpha()
    left_hand_img = pygame.transform.scale(left_hand_img, (100, 200))
except:
    print("⚠️ left_hand.png not found, using fallback.")
    left_hand_img = pygame.Surface((100, 200), pygame.SRCALPHA)
    pygame.draw.rect(left_hand_img, WHITE, (0,0,100,200))

# 2. Define EXACT Shoulder Coordinates
# These are relative to the screen center (400, 400)
# We place them slightly below and to the sides of the head
RIGHT_SHOULDER_POS = CENTER
LEFT_SHOULDER_POS = CENTER

# The pivot point *inside* the image (Bottom Center)
# This assumes the hand is drawn pointing UP. The "shoulder connection" is at the bottom.
RIGHT_HAND_PIVOT = (right_hand_img.get_width() / 2, right_hand_img.get_height())
LEFT_HAND_PIVOT = (left_hand_img.get_width() / 2, left_hand_img.get_height())

def blitRotate(surf, image, pos, originPos, angle):
    """
    Rotate and draw an image around a specific pivot point.
    """
    # 1. Create a rect for the unrotated image placed with the pivot at the target position
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    
    # 2. Get the offset vector from the image center to the pivot point
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
    # 3. Rotate the offset vector (Pygame's Vector2.rotate is CCW, so we negate the angle)
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    
    # 4. Calculate the new center of the rotated image
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    
    # 5. Rotate the actual image
    rotated_image = pygame.transform.rotate(image, angle)
    
    # 6. Get the new rect, centered at the newly calculated rotated center
    rotated_rect = rotated_image.get_rect(center=rotated_image_center)
    
    # 7. Draw it
    surf.blit(rotated_image, rotated_rect)

def draw_clock_face():
    """Draw the static clock background"""
    screen.fill(WHITE)
    
    # Outer rim
    pygame.draw.circle(screen, GRAY, CENTER, CLOCK_RADIUS + 20)
    pygame.draw.circle(screen, BLACK, CENTER, CLOCK_RADIUS + 20, 3)
    pygame.draw.circle(screen, CREAM, CENTER, CLOCK_RADIUS)
    
    # Sunburst pattern
    for i in range(36):
        angle = math.radians(i * 10)
        sx = CENTER[0] + math.cos(angle) * 50
        sy = CENTER[1] - math.sin(angle) * 50
        ex = CENTER[0] + math.cos(angle) * CLOCK_RADIUS
        ey = CENTER[1] - math.sin(angle) * CLOCK_RADIUS
        color = (255, 250, 240) if i % 2 == 0 else CREAM
        pygame.draw.line(screen, color, (sx, sy), (ex, ey), 8)
    
    # Hour marks & numbers
    font = pygame.font.Font(None, 72)
    for hour in range(1, 13):
        angle = math.radians((90 - hour * 30) % 360)
        tx1 = CENTER[0] + math.cos(angle) * (CLOCK_RADIUS - 30)
        ty1 = CENTER[1] - math.sin(angle) * (CLOCK_RADIUS - 30)
        tx2 = CENTER[0] + math.cos(angle) * (CLOCK_RADIUS - 15)
        ty2 = CENTER[1] - math.sin(angle) * (CLOCK_RADIUS - 15)
        color = RED if hour in [12, 3, 6, 9] else BLACK
        width = 4 if hour in [12, 3, 6, 9] else 3
        pygame.draw.line(screen, color, (tx1, ty1), (tx2, ty2), width)
        
        nx = CENTER[0] + math.cos(angle) * (CLOCK_RADIUS - 70)
        ny = CENTER[1] - math.sin(angle) * (CLOCK_RADIUS - 70)
        text = font.render(str(hour), True, BLACK)
        screen.blit(text, text.get_rect(center=(nx, ny)))
    
    # Minute marks
    for m in range(60):
        if m % 5 != 0:
            angle = math.radians((90 - m * 6) % 360)
            sx = CENTER[0] + math.cos(angle) * (CLOCK_RADIUS - 20)
            sy = CENTER[1] - math.sin(angle) * (CLOCK_RADIUS - 20)
            ex = CENTER[0] + math.cos(angle) * (CLOCK_RADIUS - 10)
            ey = CENTER[1] - math.sin(angle) * (CLOCK_RADIUS - 10)
            pygame.draw.line(screen, BLACK, (sx, sy), (ex, ey), 2)
    
    # Mickey Head
    pygame.draw.circle(screen, BLACK, (CENTER[0] - 80, CENTER[1] - 80), 50)  # Left ear
    pygame.draw.circle(screen, BLACK, (CENTER[0] + 80, CENTER[1] - 80), 50)  # Right ear
    pygame.draw.circle(screen, WHITE, CENTER, 100)
    pygame.draw.circle(screen, BLACK, CENTER, 100, 3)
    
    # Eyes
    pygame.draw.ellipse(screen, BLACK, (CENTER[0]-50, CENTER[1]-40, 35, 45))
    pygame.draw.ellipse(screen, BLACK, (CENTER[0]+15, CENTER[1]-40, 35, 45))
    pygame.draw.ellipse(screen, WHITE, (CENTER[0]-45, CENTER[1]-35, 25, 35))
    pygame.draw.ellipse(screen, WHITE, (CENTER[0]+20, CENTER[1]-35, 25, 35))
    pygame.draw.circle(screen, BLACK, (CENTER[0]-35, CENTER[1]-20), 8)
    pygame.draw.circle(screen, BLACK, (CENTER[0]+30, CENTER[1]-20), 8)
    
    # Nose & Smile
    pygame.draw.ellipse(screen, BLACK, (CENTER[0]-20, CENTER[1]+10, 40, 30))
    pygame.draw.arc(screen, BLACK, (CENTER[0]-40, CENTER[1]+20, 80, 40), 3.14, 6.28, 3)
    
    # Body (Red Shorts)
    pygame.draw.circle(screen, RED, (CENTER[0], CENTER[1]+180), 70)
    pygame.draw.circle(screen, WHITE, (CENTER[0]-25, CENTER[1]+170), 10)
    pygame.draw.circle(screen, WHITE, (CENTER[0]+25, CENTER[1]+170), 10)
    pygame.draw.circle(screen, WHITE, (CENTER[0]-25, CENTER[1]+190), 10)
    pygame.draw.circle(screen, WHITE, (CENTER[0]+25, CENTER[1]+190), 10)
    
    # Legs & Shoes
    pygame.draw.rect(screen, BLACK, (CENTER[0]-50, CENTER[1]+240, 35, 60))
    pygame.draw.rect(screen, BLACK, (CENTER[0]+15, CENTER[1]+240, 35, 60))
    pygame.draw.ellipse(screen, (255,255,200), (CENTER[0]-65, CENTER[1]+280, 60, 35))
    pygame.draw.ellipse(screen, (255,255,200), (CENTER[0]+5, CENTER[1]+280, 60, 35))
    pygame.draw.ellipse(screen, BLACK, (CENTER[0]-65, CENTER[1]+280, 60, 35), 2)
    pygame.draw.ellipse(screen, BLACK, (CENTER[0]+5, CENTER[1]+280, 60, 35), 2)

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Get current time
    now = datetime.now()
    minutes = now.minute
    seconds = now.second
    
    # Calculate angles: 0° = 12 o'clock, clockwise
    # Pygame rotates counter-clockwise, so we use negative values
    minute_angle = -((minutes / 60) * 360)
    second_angle = -((seconds / 60) * 360)
    
    # Draw
    draw_clock_face()
    
    # Draw Hands using the precise pivot math
    # 1. Draw Right Hand (Minutes)
    blitRotate(screen, right_hand_img, RIGHT_SHOULDER_POS, RIGHT_HAND_PIVOT, minute_angle)
    
    # 2. Draw Left Hand (Seconds)
    blitRotate(screen, left_hand_img, LEFT_SHOULDER_POS, LEFT_HAND_PIVOT, second_angle)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()