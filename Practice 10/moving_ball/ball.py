import pygame

class Ball:
    """Handles ball position, movement, and drawing"""
    
    def __init__(self, x, y, radius=25, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.move_step = 20
    
    def move_up(self, screen_height):
        """Move ball up if within bounds"""
        new_y = self.y - self.move_step
        if new_y - self.radius >= 0:
            self.y = new_y
            return True
        return False
    
    def move_down(self, screen_height):
        """Move ball down if within bounds"""
        new_y = self.y + self.move_step
        if new_y + self.radius <= screen_height:
            self.y = new_y
            return True
        return False
    
    def move_left(self, screen_width):
        """Move ball left if within bounds"""
        new_x = self.x - self.move_step
        if new_x - self.radius >= 0:
            self.x = new_x
            return True
        return False
    
    def move_right(self, screen_width):
        """Move ball right if within bounds"""
        new_x = self.x + self.move_step
        if new_x + self.radius <= screen_width:
            self.x = new_x
            return True
        return False
    
    def draw(self, screen):
        """Draw the ball on screen"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def get_position(self):
        """Get current position as tuple"""
        return (self.x, self.y)
    
    def set_position(self, x, y):
        """Set ball position"""
        self.x = x
        self.y = y