"""
Food Module - Collectible items with different weights and timers

This module contains the Food class which handles:
- Spawning food at valid grid positions
- Different food types with different point values (apple, banana, golden)
- Food that disappears after a certain time
- Ensuring food never appears on snake body or outside boundaries
- Drawing food to screen with visual indicators
"""

import pygame  # Import pygame library
import random  # Import random for position generation


class Food(pygame.sprite.Sprite):
    """
    Food class represents collectible items that make the snake grow
    
    Food types:
    - Apple: Worth 10 points, red, common (60% chance), lasts 10 seconds
    - Banana: Worth 20 points, yellow, rare (30% chance), lasts 7 seconds
    - Golden: Worth 30 points, gold, very rare (10% chance), lasts 5 seconds
    
    Food spawns on the grid and must never overlap with:
    1. The snake's body
    2. The game boundaries
    3. Disappears after timer expires
    """
    
    # Class constants for food types
    FOOD_TYPES = {
        'apple': {
            'color': (255, 0, 0), 
            'value': 10, 
            'chance': 0.6, 
            'radius': 8,
            'lifetime': 10000  # 10 seconds in milliseconds
        },
        'banana': {
            'color': (255, 255, 0), 
            'value': 20, 
            'chance': 0.3, 
            'radius': 7,
            'lifetime': 7000  # 7 seconds
        },
        'golden': {
            'color': (255, 215, 0), 
            'value': 30, 
            'chance': 0.1, 
            'radius': 10,
            'lifetime': 5000  # 5 seconds
        }
    }
    
    def __init__(self, block_size, screen_width, screen_height, snake_body):
        """
        Initialize food and spawn it at a valid position
        
        Parameters:
        block_size (int): Size of grid cells
        screen_width (int): Game window width
        screen_height (int): Game window height
        snake_body (list): List of (x, y) tuples representing snake segments
        """
        super().__init__()
        
        self.block_size = block_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Determine food type based on probability
        # random.random() returns float between 0.0 and 1.0
        rand_value = random.random()
        
        if rand_value < self.FOOD_TYPES['apple']['chance']:
            self.food_type = 'apple'
        elif rand_value < (self.FOOD_TYPES['apple']['chance'] + self.FOOD_TYPES['banana']['chance']):
            self.food_type = 'banana'
        else:
            self.food_type = 'golden'
        
        # Get properties for this food type
        food_props = self.FOOD_TYPES[self.food_type]
        self.value = food_props['value']  # Points this food is worth
        self.color = food_props['color']  # Color for drawing
        self.radius = food_props['radius']  # Size of the food
        self.lifetime = food_props['lifetime']  # How long it lasts (ms)
        
        # Record spawn time
        # pygame.time.get_ticks() returns milliseconds since pygame.init()
        self.spawn_time = pygame.time.get_ticks()
        
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
        
        Also resets the spawn time for the timer.
        
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
                # Reset spawn time for new position
                self.spawn_time = pygame.time.get_ticks()
                break  # Exit while loop
    
    def is_expired(self):
        """
        Check if food has exceeded its lifetime
        
        Returns:
        bool: True if food should disappear, False otherwise
        """
        # Get current time in milliseconds
        current_time = pygame.time.get_ticks()
        
        # Calculate how long food has been on screen
        elapsed_time = current_time - self.spawn_time
        
        # Return True if elapsed time exceeds lifetime
        return elapsed_time >= self.lifetime
    
    def get_remaining_time(self):
        """
        Get remaining time before food disappears
        
        Returns:
        int: Milliseconds remaining (0 if expired)
        """
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.spawn_time
        remaining = self.lifetime - elapsed
        
        # Return 0 if already expired (no negative values)
        return max(0, remaining)
    
    def draw(self, screen):
        """
        Draw food as a circle with optional timer indicator
        
        Parameters:
        screen: Pygame display surface to draw on
        """
        # Calculate center of the food's grid cell
        # Add half block_size to x and y to center the circle
        center = (self.position[0] + self.block_size // 2,
                 self.position[1] + self.block_size // 2)
        
        # Draw filled circle with food color
        pygame.draw.circle(screen, self.color, center, self.radius)
        
        # Draw black outline for visibility
        pygame.draw.circle(screen, (0, 0, 0), center, self.radius, 2)
        
        # Draw timer indicator for rare foods (banana and golden)
        if self.food_type in ['banana', 'golden']:
            # Calculate remaining time as percentage
            remaining_pct = self.get_remaining_time() / self.lifetime
            
            # Draw shrinking circle to show time remaining
            if remaining_pct > 0:
                timer_radius = int(self.radius * remaining_pct)
                # Draw semi-transparent timer circle
                timer_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(timer_surface, (255, 255, 255, 128), 
                                 (self.radius, self.radius), timer_radius)
                screen.blit(timer_surface, (self.position[0], self.position[1]))
    
    def get_position(self):
        """
        Return current food position
        
        Used by main game loop to check collision with snake head
        Returns:
        tuple: (x, y) coordinates of food
        """
        return self.position