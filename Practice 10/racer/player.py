"""
Player Module - Controls the player's car

This module contains the Player class which handles:
- Creating the player car sprite
- Moving the car left and right based on keyboard input
- Keeping the car within screen boundaries
"""

import pygame  # Import pygame library for game development


class Player(pygame.sprite.Sprite):
    """
    Player class represents the user-controlled car
    
    Inherits from pygame.sprite.Sprite to use built-in sprite features:
    - image: The visual representation of the sprite
    - rect: The rectangular boundary for collision detection
    """
    
    def __init__(self, x, y):
        """
        Initialize the player car
        
        Parameters:
        x (int): Starting x-coordinate (horizontal position)
        y (int): Starting y-coordinate (vertical position)
        """
        # Call parent class (Sprite) constructor to initialize sprite properties
        super().__init__()
        
        # Create a surface (image) for the car - 50 pixels wide, 100 pixels tall
        # This is a placeholder - you can replace with pygame.image.load("car.png")
        self.image = pygame.Surface((50, 100))
        
        # Fill the surface with red color (RGB: 255, 0, 0)
        # This makes the car visible on screen
        self.image.fill((255, 0, 0))
        
        # Get the rectangular boundary of the car
        # The rect is used for positioning and collision detection
        # center=(x, y) places the car at the specified coordinates
        self.rect = self.image.get_rect(center=(x, y))
        
        # Set movement speed: 5 pixels per frame
        # Higher values = faster movement, lower = slower
        self.speed = 5
    
    def update(self, keys, screen_width):
        """
        Update player position based on keyboard input
        
        This method is called every frame to check for key presses
        and move the car accordingly.
        
        Parameters:
        keys (dict): Dictionary of keyboard state from pygame.key.get_pressed()
                    Returns True for pressed keys, False otherwise
        screen_width (int): Width of the game screen for boundary checking
        """
        # Check if LEFT arrow key is pressed
        # AND if the car's left edge is greater than 0 (not at screen edge)
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            # Move car left by decreasing x-coordinate
            # self.speed determines how many pixels to move per frame
            self.rect.x -= self.speed
        
        # Check if RIGHT arrow key is pressed
        # AND if the car's right edge is less than screen width (not at edge)
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            # Move car right by increasing x-coordinate
            self.rect.x += self.speed