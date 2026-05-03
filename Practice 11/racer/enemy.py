"""
Enemy Module - Controls enemy cars with image support

This module handles:
- Loading enemy car images (with transparency)
- Falling back to colored rectangles if images fail
- Moving enemies down the screen
- Removing enemies when off-screen
"""

import pygame
import random
import os


class Enemy(pygame.sprite.Sprite):
    """
    Enemy class represents cars that the player must avoid
    
    Features:
    - Loads custom images with automatic transparency
    - Falls back to blue rectangles if images missing
    - Variable speed based on game difficulty
    """
    
    def __init__(self, screen_width, road_left, road_right, base_speed, image_path=None):
        """
        Initialize an enemy car
        
        Parameters:
        screen_width (int): Width of game screen
        road_left (int): Left boundary of road
        road_right (int): Right boundary of road
        base_speed (int): Base movement speed
        image_path (str, optional): Path to enemy car image file
        """
        super().__init__()
        
        # Try to load custom enemy car image
        image_loaded = False
        
        if image_path:
            if os.path.exists(image_path):
                try:
                    # Load image
                    self.original_image = pygame.image.load(image_path)
                    
                    # Handle transparency:
                    # Method 1: If image has alpha channel, use it
                    if self.original_image.get_alpha():
                        self.original_image = self.original_image.convert_alpha()
                    else:
                        # Method 2: Make white background transparent
                        self.original_image = self.original_image.convert()
                        self.original_image.set_colorkey((255, 255, 255))
                    
                    # Scale to standard size (50x100 pixels)
                    self.original_image = pygame.transform.scale(self.original_image, (50, 100))
                    
                    # Create a copy for rendering
                    self.image = self.original_image.copy()
                    
                    print(f"✅ Enemy image loaded: {image_path}")
                    image_loaded = True
                    
                except pygame.error as e:
                    print(f"⚠️ Could not load enemy image: {e}")
                    print(f"   Using fallback rectangle instead")
            else:
                print(f"⚠️ Enemy image not found: {image_path}")
                print(f"   Using fallback rectangle instead")
        
        # If image loading failed, create fallback rectangle
        if not image_loaded:
            self._create_fallback_car()
        
        # Spawn enemy at random x-position within road boundaries
        spawn_x = random.randint(road_left, road_right - 50)
        
        # Set the rectangular boundary for collision detection
        self.rect = self.image.get_rect(center=(spawn_x, -100))
        # y = -100 starts enemy completely above visible screen
        
        # Set speed: base_speed ± small random variation (±1)
        # Ensures minimum speed of 2
        self.speed = max(2, base_speed + random.randint(-1, 1))
    
    def _create_fallback_car(self):
        """
        Create a simple colored rectangle as fallback when image fails
        
        Draws a blue rectangle with a green "windshield" for visual interest
        """
        # Create surface (50 pixels wide, 100 pixels tall)
        self.original_image = pygame.Surface((50, 100))
        
        # Fill with blue color (RGB: 0, 0, 255)
        self.original_image.fill((0, 0, 255))
        
        # Draw a "windshield" for visual distinction
        # Light green rectangle at top
        pygame.draw.rect(self.original_image, (100, 255, 100), (10, 10, 30, 20))
        
        # Create copy for rendering
        self.image = self.original_image.copy()
    
    def update(self):
        """
        Update enemy position by moving it down the screen
        
        Called automatically every frame by the sprite group.
        Removes enemy when it exits the bottom of the screen.
        """
        # Move enemy down by increasing y-coordinate
        self.rect.y += self.speed
        
        # Check if enemy has moved completely off-screen
        # When top edge is below screen height (800), remove it
        if self.rect.top > 800:
            # Remove from all sprite groups and free memory
            self.kill()