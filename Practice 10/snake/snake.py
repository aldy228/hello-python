"""
Snake Module - Core game logic for the snake

This module contains the Snake class which handles:
- Snake movement on a grid system
- Direction changes (with anti-reverse protection)
- Collision detection (walls and self)
- Growth mechanics
- Drawing to screen
"""

import pygame  # Import pygame library
import random  # Import random for initial direction (optional)


class Snake:
    """
    Snake class represents the player-controlled snake
    
    The snake is stored as a list of coordinate tuples:
    [(head_x, head_y), (body1_x, body1_y), (body2_x, body2_y), ...]
    Index 0 is always the head, last index is the tail.
    """
    
    def __init__(self, block_size, screen_width, screen_height):
        """
        Initialize the snake with default position and properties
        
        Parameters:
        block_size (int): Size of each grid cell in pixels
        screen_width (int): Width of game window
        screen_height (int): Height of game window
        """
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize snake body with 3 segments starting near center
        # Each tuple represents (x, y) coordinates of a block
        # Head is at index 0, tail grows at the end
        self.body = [
            (screen_width // 2, screen_height // 2),  # Head
            (screen_width // 2 - block_size, screen_height // 2),  # Body segment 1
            (screen_width // 2 - 2 * block_size, screen_height // 2)  # Body segment 2
        ]
        
        # Direction vector: (x_change, y_change)
        # (1, 0) means moving right, (-1, 0) left, (0, -1) up, (0, 1) down
        self.direction = (1, 0)  # Start moving right
        
        # Flag to track if snake should grow on next move
        # Prevents growing every frame; only grows when food is eaten
        self.grow_pending = False
        
        # Snake color (bright green)
        self.color = (0, 200, 0)
    
    def change_direction(self, new_direction):
        """
        Change snake's movement direction
        
        Implements anti-reverse logic: snake cannot turn 180° into itself
        Example: If moving right (1, 0), cannot immediately change to left (-1, 0)
        
        Parameters:
        new_direction (tuple): Desired direction as (x, y) vector
        """
        # Calculate opposite of current direction
        # Multiplying by -1 reverses the vector
        opposite_direction = (self.direction[0] * -1, self.direction[1] * -1)
        
        # Only change direction if new direction is NOT the opposite
        # This prevents the snake from instantly colliding with its own neck
        if new_direction != opposite_direction:
            self.direction = new_direction
    
    def move(self):
        """
        Move snake one grid step in current direction
        
        Movement logic:
        1. Calculate new head position based on direction
        2. Insert new head at beginning of body list
        3. Remove tail UNLESS snake is growing
        """
        # Get current head coordinates
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        
        # Calculate new head position
        # Multiply direction by block_size to move exactly one grid cell
        new_head = (head_x + dir_x * self.block_size, 
                   head_y + dir_y * self.block_size)
        
        # Insert new head at front of list (index 0)
        # This shifts all existing body segments back by one position
        self.body.insert(0, new_head)
        
        # Check if snake should grow
        if not self.grow_pending:
            # Remove last element (tail) to maintain current length
            # pop() without arguments removes and returns the last item
            self.body.pop()
        else:
            # Keep tail (snake grows by 1 segment)
            # Reset flag so next move doesn't grow again
            self.grow_pending = False
    
    def grow(self):
        """
        Mark snake to grow on next movement
        
        Instead of immediately adding a segment, we set a flag.
        The next move() call will skip removing the tail, effectively growing.
        This keeps movement and growth logic synchronized.
        """
        self.grow_pending = True
    
    def check_collision(self):
        """
        Check if snake has collided with walls or itself
        
        Returns:
        bool: True if collision occurred (game over), False otherwise
        """
        # Get head position for collision checks
        head = self.body[0]
        
        # WALL COLLISION CHECK
        # Check if head x-coordinate is outside left or right boundaries
        # Check if head y-coordinate is outside top or bottom boundaries
        # >= screen_width means it's at or past the right edge
        if (head[0] < 0 or head[0] >= self.screen_width or
            head[1] < 0 or head[1] >= self.screen_height):
            return True  # Hit a wall
        
        # SELF-COLLISION CHECK
        # Check if head position matches ANY body segment except itself
        # self.body[1:] creates a new list excluding the head (index 0)
        # The 'in' operator checks if head tuple exists in the body list
        if head in self.body[1:]:
            return True  # Hit itself
        
        # No collision detected
        return False
    
    def draw(self, screen):
        """
        Draw all snake segments on the screen
        
        Parameters:
        screen: Pygame display surface to draw on
        """
        # Loop through each segment in the snake's body
        for segment in self.body:
            # Draw rectangle for each segment
            # segment is (x, y), so *segment unpacks it as x, y
            # width and height are both block_size to make squares
            pygame.draw.rect(screen, self.color, 
                           (*segment, self.block_size, self.block_size))
            
            # Draw black outline around each segment
            # width=2 makes a 2-pixel border
            pygame.draw.rect(screen, (0, 0, 0), 
                           (*segment, self.block_size, self.block_size), 2)
    
    def get_head(self):
        """
        Return the current head position tuple
        
        Used by main game loop to check food collision
        Returns:
        tuple: (x, y) coordinates of snake head
        """
        return self.body[0]