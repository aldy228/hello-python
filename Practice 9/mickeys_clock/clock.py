import pygame
import os
from datetime import datetime
import math

class MickeysClock:
    """Handles clock logic and hand rotation"""
    
    def __init__(self, image_path):
        self.center = (0, 0)  # Will be set later
        self.load_hand_image(image_path)
    
    def load_hand_image(self, path):
        """Load Mickey hand image with fallback"""
        try:
            self.hand_image = pygame.image.load(path).convert_alpha()
            self.hand_image = pygame.transform.scale(self.hand_image, (100, 300))
        except FileNotFoundError:
            print(f"Warning: Image not found at {path}")
            # Create placeholder
            self.hand_image = pygame.Surface((100, 300), pygame.SRCALPHA)
            pygame.draw.rect(self.hand_image, (0, 0, 0), (0, 0, 100, 300))
    
    def set_center(self, x, y):
        """Set clock center position"""
        self.center = (x, y)
    
    def get_current_time(self):
        """Get current minutes and seconds"""
        now = datetime.now()
        return now.minute, now.second
    
    def calculate_angle(self, value, max_value):
        """
        Convert time value to rotation angle
        0 degrees = 12 o'clock (pointing up)
        Clockwise rotation is negative in Pygame
        """
        return -(value / max_value) * 360
    
    def rotate_hand(self, angle):
        """
        Rotate hand image around its bottom center
        Returns rotated image and its rectangle
        """
        rotated = pygame.transform.rotate(self.hand_image, angle)
        new_rect = rotated.get_rect(center=(self.center[0], self.center[1]))
        return rotated, new_rect
    
    def get_minute_hand(self):
        """Get rotated minute hand (right hand)"""
        minutes, _ = self.get_current_time()
        angle = self.calculate_angle(minutes, 60)
        return self.rotate_hand(angle)
    
    def get_second_hand(self):
        """Get rotated second hand (left hand)"""
        _, seconds = self.get_current_time()
        angle = self.calculate_angle(seconds, 60)
        return self.rotate_hand(angle)