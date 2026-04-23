"""
Coin Module - Collectible items for bonus points

This module contains the Coin class which handles:
- Creating coin sprites at random positions WITHIN road boundaries
- Moving coins down the screen
- Automatic removal when off-screen
"""

import pygame  # Import pygame library
import random  # Import random for random positioning


class Coin(pygame.sprite.Sprite):
    """
    Coin class represents collectible items that give bonus points
    
    Coins appear randomly on the road and move downward.
    When the player's car touches a coin, it's collected for points.
    """
    
    def __init__(self, screen_width, road_left, road_right):
        """
        Initialize a coin at a random horizontal position within road
        
        Parameters:
        screen_width (int): Width of the game screen
        road_left (int): Left boundary of the road
        road_right (int): Right boundary of the road
        """
        # Call parent class constructor
        super().__init__()
        
        # Create a transparent surface for the coin
        # Size: 30x30 pixels (smaller than cars for visual variety)
        # pygame.SRCALPHA flag enables per-pixel transparency
        # This allows us to draw a circle without a rectangular background
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Draw a yellow circle on the surface to represent a coin
        # Parameters:
        # - self.image: Surface to draw on
        # - (255, 215, 0): Gold/Yellow color in RGB
        # - (15, 15): Center point of circle (middle of 30x30 surface)
        # - 15: Radius of circle (half the surface size)
        pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
        
        # FIXED: Spawn coin within road boundaries
        spawn_x = random.randint(road_left, road_right - 30)
        
        self.rect = self.image.get_rect(
            center=(spawn_x, -50)  # Start above screen
        )
        # y = -50 starts coin 50 pixels above visible screen
        # Creates smooth entrance effect
        
        # Set movement speed to 4 pixels per frame
        # Slightly slower than some enemies for gameplay balance
        self.speed = 4
    
    def update(self):
        """
        Update coin position by moving it down the screen
        
        Called every frame to animate the coin falling.
        Removes coin when it exits the bottom of the screen.
        """
        # Move coin down by increasing y-coordinate
        self.rect.y += self.speed
        
        # Check if coin has moved completely off-screen
        # When top edge is below screen height (800), remove it
        if self.rect.top > 800:
            # Remove coin from sprite groups to free memory
            self.kill()