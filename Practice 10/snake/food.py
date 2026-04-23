"""
Food Module - Collectible items for snake growth

This module contains the Food class which handles:
- Spawning food at valid grid positions
- Ensuring food never appears on snake body or outside boundaries
- Drawing food to screen
"""

import pygame  # Import pygame library
import random  # Import random for position generation


class Food:
    """
    Food class represents collectible items that make the snake grow
    
    Food spawns on the grid and must never overlap with:
    1. The snake's body
    2. The game boundaries
    """
    
    def __init__(self, block_size, screen_width, screen_height, snake_body):
        """
        Initialize food and spawn it at a valid position
        
        Parameters:
        block_size (int): Size of grid cells
        screen_width (int): Game window width
        screen_height (int): Game window height
        snake_body (list): List of (x, y) tuples representing snake segments
        """
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = (255, 0, 0)  # Red color for food
        self.position = (0, 0)  # Will be set by respawn()
        
        # Generate initial position that doesn't overlap snake
        self.respawn(snake_body)
    
    def respawn(self, snake_body):
        """
        Generate a new random position for food
        
        Uses a while loop to keep generating positions until a valid one is found.
        Valid means:
        - Aligned to grid (multiples of block_size)
        - Inside screen boundaries
        - Not overlapping any snake segment
        
        Parameters:
        snake_body (list): Current snake body positions to avoid
        """
        # Infinite loop that only breaks when valid position is found
        while True:
            # Calculate valid grid positions
            # (screen_width - block_size) // block_size gives max index
            # Multiply by block_size to snap to grid
            x = random.randint(0, (self.screen_width - self.block_size) // self.block_size) * self.block_size
            y = random.randint(0, (self.screen_height - self.block_size) // self.block_size) * self.block_size
            
            # Check if generated position overlaps with any snake segment
            # If (x, y) is NOT in snake_body, position is valid
            if (x, y) not in snake_body:
                # Save valid position and exit loop
                self.position = (x, y)
                break  # Exit while loop
    
    def draw(self, screen):
        """
        Draw food as a circle centered in its grid cell
        
        Parameters:
        screen: Pygame display surface to draw on
        """
        # Calculate center of the food's grid cell
        # Add half block_size to x and y to center the circle
        center = (self.position[0] + self.block_size // 2,
                 self.position[1] + self.block_size // 2)
        
        # Draw filled red circle
        # Radius is half the block size to fit perfectly in cell
        pygame.draw.circle(screen, self.color, center, self.block_size // 2)
        
        # Draw black outline for visibility
        # width=2 creates a 2-pixel border
        pygame.draw.circle(screen, (0, 0, 0), center, self.block_size // 2, 2)
    
    def get_position(self):
        """
        Return current food position
        
        Used by main game loop to check collision with snake head
        Returns:
        tuple: (x, y) coordinates of food
        """
        return self.position