"""
Player Module - Controls the player's car

Updated: Movement now respects road boundaries (not screen edges).
"""

import pygame
import os


class Player(pygame.sprite.Sprite):
    """Player car with image support"""
    
    def __init__(self, x, y, image_path=None):
        super().__init__()
        
        image_loaded = False
        
        if image_path:
            if os.path.exists(image_path):
                try:
                    self.original_image = pygame.image.load(image_path)
                    if self.original_image.get_alpha():
                        self.original_image = self.original_image.convert_alpha()
                    else:
                        self.original_image = self.original_image.convert()
                        self.original_image.set_colorkey((255, 255, 255))
                    self.original_image = pygame.transform.scale(self.original_image, (50, 100))
                    self.image = self.original_image.copy()
                    image_loaded = True
                except:
                    self._create_fallback()
            else:
                self._create_fallback()
        else:
            self._create_fallback()
        
        # CRITICAL: Create rect for collision
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
    
    def _create_fallback(self):
        """Create red rectangle fallback"""
        self.original_image = pygame.Surface((50, 100))
        self.original_image.fill((255, 0, 0))
        pygame.draw.rect(self.original_image, (100, 100, 255), (10, 10, 30, 20))
        self.image = self.original_image.copy()
    
    def update(self, keys, screen_width):
        """
        Update player position
        Note: Road boundary checking is now done in main.py
        """
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed