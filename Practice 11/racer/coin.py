"""
Coin Module - Collectible items with different weights/values

Updated to accept custom speed parameter for level-based scaling.
"""

import pygame
import random


class Coin(pygame.sprite.Sprite):
    """Coin with gold/silver/bronze types and configurable speed"""
    
    COIN_TYPES = {
        'gold': {'color': (255, 215, 0), 'value': 10, 'chance': 0.6, 'radius': 15},
        'silver': {'color': (192, 192, 192), 'value': 5, 'chance': 0.3, 'radius': 12},
        'bronze': {'color': (205, 127, 50), 'value': 3, 'chance': 0.1, 'radius': 10}
    }
    
    def __init__(self, screen_width, road_left, road_right, coin_speed=4, image_path=None):
        """
        Initialize coin
        
        NEW PARAMETER:
        coin_speed (float): Movement speed (increases with level)
        """
        super().__init__()
        
        # Determine coin type
        rand_value = random.random()
        if rand_value < self.COIN_TYPES['gold']['chance']:
            self.coin_type = 'gold'
        elif rand_value < (self.COIN_TYPES['gold']['chance'] + self.COIN_TYPES['silver']['chance']):
            self.coin_type = 'silver'
        else:
            self.coin_type = 'bronze'
        
        coin_props = self.COIN_TYPES[self.coin_type]
        self.value = coin_props['value']
        self.radius = coin_props['radius']
        
        # Try to load custom image
        if image_path and hasattr(pygame, 'image') and pygame.image:
            try:
                import os
                if os.path.exists(image_path):
                    self.original_image = pygame.image.load(image_path).convert_alpha()
                    self.original_image = pygame.transform.scale(self.original_image, (self.radius*2, self.radius*2))
                    # Make white transparent if needed
                    if not self.original_image.get_alpha():
                        self.original_image.set_colorkey((255, 255, 255))
                    self.image = self.original_image.copy()
                else:
                    self._create_fallback()
            except:
                self._create_fallback()
        else:
            self._create_fallback()
        
        # Spawn within road
        spawn_x = random.randint(road_left + self.radius, road_right - self.radius)
        self.rect = self.image.get_rect(center=(spawn_x, -self.radius * 2))
        
        # === NEW: Use passed speed parameter ===
        self.speed = coin_speed
    
    def _create_fallback(self):
        """Create colored circle fallback"""
        coin_props = self.COIN_TYPES[self.coin_type]
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, coin_props['color'], (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, (0, 0, 0), (self.radius, self.radius), self.radius, 2)
    
    def update(self):
        """Move coin down; remove if off-screen"""
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()