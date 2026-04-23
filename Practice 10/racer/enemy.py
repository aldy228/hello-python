"""
Enemy Module - Controls enemy cars

This module contains the Enemy class which handles:
- Creating enemy car sprites at random positions WITHIN road boundaries
- Moving enemies down the screen
- Removing enemies when they exit the screen
"""

import pygame  # Import pygame for game functionality
import random  # Import random module for generating random positions


class Enemy(pygame.sprite.Sprite):
    """
    Enemy class represents cars that the player must avoid
    
    These cars spawn at the top of the screen and move downward
    at varying speeds to create challenge for the player.
    """
    
    def __init__(self, screen_width, road_left, road_right):
        """
        Initialize an enemy car at a random position within road boundaries
        
        Parameters:
        screen_width (int): Width of the game screen
        road_left (int): Left boundary of the road (x-coordinate)
        road_right (int): Right boundary of the road (x-coordinate)
        """
        # Call parent class constructor
        super().__init__()
        
        # Create enemy car surface - 50x100 pixels (same size as player)
        self.image = pygame.Surface((50, 100))
        
        # Fill with blue color (RGB: 0, 0, 255) to distinguish from player
        # Player is red, enemies are blue for visual clarity
        self.image.fill((0, 0, 255))
        
        # FIXED: Spawn enemy at random x-position WITHIN road boundaries
        # road_left + padding to road_right - padding ensures full visibility
        spawn_x = random.randint(road_left, road_right - 50)
        
        self.rect = self.image.get_rect(
            center=(spawn_x, -100)  # Start above screen
        )
        # y = -100 means the car starts 100 pixels ABOVE the visible screen
        # This creates a smooth entrance as it moves down into view
        
        # Random speed between 3 and 7 pixels per frame
        # Varying speeds make the game more challenging and unpredictable
        # Slower enemies (3) are easier to avoid
        # Faster enemies (7) require quicker reactions
        self.speed = random.randint(3, 7)
    
    def update(self):
        """
        Update enemy position by moving it down the screen
        
        This method is called every frame by the sprite group.
        It moves the enemy downward and removes it when it exits the screen.
        """
        # Move enemy down by increasing y-coordinate
        # Positive y movement = downward in pygame coordinate system
        self.rect.y += self.speed
        
        # Check if enemy has moved completely off the bottom of screen
        # self.rect.top is the y-coordinate of the top edge of the enemy
        # 800 is the screen height - when top > 800, entire enemy is below screen
        if self.rect.top > 800:
            # Remove enemy from all sprite groups
            # self.kill() is a built-in Sprite method that:
            # - Removes sprite from all groups it belongs to
            # - Frees up memory
            # - Prevents unnecessary updates to off-screen objects
            self.kill()