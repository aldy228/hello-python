"""
Tools Module - Drawing functionality for Paint app

This module contains the DrawingTools class which handles:
- Brush drawing (freehand lines) with gap prevention
- Shape drawing (rectangles and circles) with preview system
- Eraser functionality
- Tool and color state management
"""

import pygame  # Import pygame library


class DrawingTools:
    """
    DrawingTools class manages all drawing operations on a surface
    
    Maintains state for:
    - Current tool (brush, rect, circle, eraser)
    - Current color
    - Brush/eraser size
    - Drawing state (is mouse currently held down?)
    - Starting position for shapes
    - Last position for continuous brush strokes
    """
    
    def __init__(self, canvas, preview_surface):
        """
        Initialize drawing tools
        
        Parameters:
        canvas: Pygame Surface for permanent drawings
        preview_surface: Pygame Surface for temporary shape previews (ghost shapes)
        """
        self.canvas = canvas  # Main drawing surface
        self.preview_surface = preview_surface  # Temporary overlay for shapes
        self.color = (0, 0, 0)  # Default color: black
        self.brush_size = 5  # Default brush radius in pixels
        self.tool = "brush"  # Default active tool
        self.drawing = False  # Track if mouse button is held down
        self.start_pos = None  # Store starting position for shapes
        self.last_pos = None  # Store last mouse position for smooth brush strokes
    
    def set_color(self, color):
        """
        Change the current drawing color
        
        Parameters:
        color (tuple): RGB color tuple (R, G, B)
        """
        self.color = color
    
    def set_brush_size(self, size):
        """
        Change brush and eraser size
        
        Parameters:
        size (int): Radius in pixels
        """
        self.brush_size = size
    
    def set_tool(self, tool_name):
        """
        Switch between drawing tools
        
        Parameters:
        tool_name (str): One of "brush", "rect", "circle", "eraser"
        """
        self.tool = tool_name
    
    def start_drawing(self, pos):
        """
        Begin drawing operation at given position
        
        Called when mouse button is pressed.
        Records starting position for shape tools.
        
        Parameters:
        pos (tuple): (x, y) coordinates where drawing starts
        """
        self.drawing = True
        self.start_pos = pos
        self.last_pos = pos  # Initialize last position for brush strokes
        
        # Clear the preview surface (remove old ghost shapes)
        self.preview_surface.fill((0, 0, 0, 0))  # Transparent fill
        
        # If brush/eraser, draw immediately at start position
        if self.tool in ["brush", "eraser"]:
            self.draw_on_canvas(pos)
    
    def update_preview(self, pos):
        """
        Update the 'ghost' shape while dragging mouse
        
        This is called continuously while mouse moves with button held.
        Only applies to shape tools (rect, circle).
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        if not self.drawing:
            return
        
        # Only preview shapes (Rect, Circle)
        if self.tool in ["rect", "circle"]:
            # Clear old preview by filling with transparent color
            self.preview_surface.fill((0, 0, 0, 0))
            
            if self.tool == "rect":
                # Calculate width and height from start to current position
                # Can be negative if dragging left/up, which pygame handles correctly
                width = pos[0] - self.start_pos[0]
                height = pos[1] - self.start_pos[1]
                
                # Draw rectangle outline on preview surface
                # width=2 makes a 2-pixel border (0 would fill it)
                pygame.draw.rect(self.preview_surface, self.color, 
                               (self.start_pos[0], self.start_pos[1], width, height), 2)
            
            elif self.tool == "circle":
                # Calculate radius using Pythagorean theorem
                # distance = sqrt((x2-x1)^2 + (y2-y1)^2)
                radius = int(((pos[0] - self.start_pos[0])**2 + 
                             (pos[1] - self.start_pos[1])**2)**0.5)
                
                # Draw circle outline centered at start position
                # radius=0 would fill it, radius=2 draws outline
                pygame.draw.circle(self.preview_surface, self.color, self.start_pos, radius, 2)
    
    def draw(self, pos):
        """
        Draw based on current tool and position
        
        This method is called repeatedly while mouse moves with button held.
        Uses pygame.draw.line to connect points and prevent gaps.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
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
        """
        End drawing operation and stamp shapes onto canvas
        
        Called when mouse button is released.
        For shapes, this commits the preview to the main canvas.
        
        Parameters:
        pos (tuple): Final (x, y) mouse coordinates
        """
        if not self.drawing:
            return

        # If it was a shape, stamp the preview onto the main canvas
        if self.tool in ["rect", "circle"]:
            self.canvas.blit(self.preview_surface, (0, 0))
        
        # Reset state
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_surface.fill((0, 0, 0, 0))  # Clean up preview