import pygame

class DrawingTools:
    def __init__(self, canvas, preview_surface):
        self.canvas = canvas
        self.preview_surface = preview_surface
        self.color = (0, 0, 0)
        self.brush_size = 5
        self.tool = "brush"
        self.drawing = False
        self.start_pos = None
        self.last_pos = None  # Track last position to connect lines
    
    def set_color(self, color):
        self.color = color
    
    def set_brush_size(self, size):
        self.brush_size = size
    
    def set_tool(self, tool_name):
        self.tool = tool_name
    
    def start_drawing(self, pos):
        """Called when mouse button is pressed"""
        self.drawing = True
        self.start_pos = pos
        self.last_pos = pos  # Initialize last_pos
        
        # Clear preview surface
        self.preview_surface.fill((0, 0, 0, 0))
        
        # Draw a single dot at the start
        if self.tool == "brush":
            pygame.draw.circle(self.canvas, self.color, pos, self.brush_size)
        elif self.tool == "eraser":
            pygame.draw.circle(self.canvas, (255, 255, 255), pos, self.brush_size * 2)

    def update_preview(self, pos):
        """Called when mouse moves (for Shapes only)"""
        if not self.drawing:
            return
        
        if self.tool in ["rect", "circle"]:
            self.preview_surface.fill((0, 0, 0, 0)) # Clear ghost
            
            if self.tool == "rect":
                w = pos[0] - self.start_pos[0]
                h = pos[1] - self.start_pos[1]
                pygame.draw.rect(self.preview_surface, self.color, 
                               (self.start_pos[0], self.start_pos[1], w, h), 2)
            
            elif self.tool == "circle":
                r = int(((pos[0] - self.start_pos[0])**2 + (pos[1] - self.start_pos[1])**2)**0.5)
                pygame.draw.circle(self.preview_surface, self.color, self.start_pos, r, 2)

    def draw(self, pos):
        """Called when mouse moves (for Brush/Eraser)"""
        if not self.drawing:
            return
            
        # FIX: Draw a line from last position to current position
        # This fills the gaps when moving the mouse quickly
        if self.tool == "brush":
            pygame.draw.line(self.canvas, self.color, self.last_pos, pos, self.brush_size * 2)
        elif self.tool == "eraser":
            pygame.draw.line(self.canvas, (255, 255, 255), self.last_pos, pos, self.brush_size * 4)
        
        # Update last position to current for the next frame
        self.last_pos = pos

    def finish_drawing(self, pos):
        """Called when mouse button is released"""
        if not self.drawing:
            return

        # If shape tool, stamp the preview onto the canvas
        if self.tool in ["rect", "circle"]:
            self.canvas.blit(self.preview_surface, (0, 0))
        
        # Reset state
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_surface.fill((0, 0, 0, 0))