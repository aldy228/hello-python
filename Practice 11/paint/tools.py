"""
Tools Module - Drawing functionality for Paint app (Enhanced)

This module contains the DrawingTools class which handles:
- Brush drawing (freehand lines) with gap prevention
- Shape drawing (rectangles, circles, squares, triangles, rhombus) with preview system
- Eraser functionality
- Tool and color state management

NEW SHAPES:
- Square: Equal width and height rectangle
- Right Triangle: Triangle with 90-degree angle
- Equilateral Triangle: Triangle with all sides equal
- Rhombus: Diamond shape with equal sides
"""

import pygame  # Import pygame library
import math  # Import math for trigonometric calculations


class DrawingTools:
    """
    DrawingTools class manages all drawing operations on a surface
    
    Maintains state for:
    - Current tool (brush, rect, circle, square, right_triangle, equilateral_triangle, rhombus, eraser)
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
        tool_name (str): One of "brush", "rect", "circle", "square", 
                        "right_triangle", "equilateral_triangle", "rhombus", "eraser"
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
            self._draw_brush_or_eraser(pos)
    
    def update_preview(self, pos):
        """
        Update the 'ghost' shape while dragging mouse
        
        This is called continuously while mouse moves with button held.
        Only applies to shape tools (rect, circle, square, triangles, rhombus).
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        if not self.drawing:
            return
        
        # Only preview shapes
        if self.tool in ["rect", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"]:
            # Clear old preview by filling with transparent color
            self.preview_surface.fill((0, 0, 0, 0))
            
            if self.tool == "rect":
                self._draw_rect_preview(pos)
            elif self.tool == "circle":
                self._draw_circle_preview(pos)
            elif self.tool == "square":
                self._draw_square_preview(pos)
            elif self.tool == "right_triangle":
                self._draw_right_triangle_preview(pos)
            elif self.tool == "equilateral_triangle":
                self._draw_equilateral_triangle_preview(pos)
            elif self.tool == "rhombus":
                self._draw_rhombus_preview(pos)
    
    def _draw_rect_preview(self, pos):
        """
        Draw rectangle outline on preview surface
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Calculate width and height from start to current position
        width = pos[0] - self.start_pos[0]
        height = pos[1] - self.start_pos[1]
        
        # Draw rectangle outline on preview surface
        pygame.draw.rect(self.preview_surface, self.color, 
                       (self.start_pos[0], self.start_pos[1], width, height), 2)
    
    def _draw_circle_preview(self, pos):
        """
        Draw circle outline on preview surface
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Calculate radius using Pythagorean theorem
        radius = int(((pos[0] - self.start_pos[0])**2 + 
                     (pos[1] - self.start_pos[1])**2)**0.5)
        
        # Draw circle outline centered at start position
        pygame.draw.circle(self.preview_surface, self.color, self.start_pos, radius, 2)
    
    def _draw_square_preview(self, pos):
        """
        Draw square outline on preview surface
        
        A square is a rectangle with equal width and height.
        We use the larger dimension to ensure it's a perfect square.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Calculate width and height
        width = pos[0] - self.start_pos[0]
        height = pos[1] - self.start_pos[1]
        
        # Use the smaller absolute value to ensure perfect square
        size = min(abs(width), abs(height))
        
        # Adjust sign based on direction
        if width < 0:
            size = -size
        
        # Draw square outline
        pygame.draw.rect(self.preview_surface, self.color,
                       (self.start_pos[0], self.start_pos[1], size, size), 2)
    
    def _draw_right_triangle_preview(self, pos):
        """
        Draw right triangle outline on preview surface
        
        A right triangle has one 90-degree angle.
        The right angle is at the starting position.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Define the three points of the triangle
        # Point 1: Start position (right angle)
        p1 = self.start_pos
        # Point 2: Same x as start, y as current (vertical line)
        p2 = (self.start_pos[0], pos[1])
        # Point 3: Current position (horizontal line from p2)
        p3 = pos
        
        # Draw triangle outline using polygon
        # width=2 makes a 2-pixel border
        pygame.draw.polygon(self.preview_surface, self.color, [p1, p2, p3], 2)
    
    def _draw_equilateral_triangle_preview(self, pos):
        """
        Draw equilateral triangle outline on preview surface
        
        An equilateral triangle has all sides equal and all angles 60 degrees.
        We calculate the third point using trigonometry.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Calculate the base length from start to current position
        base_length = int(((pos[0] - self.start_pos[0])**2 + 
                          (pos[1] - self.start_pos[1])**2)**0.5)
        
        # Calculate the height of an equilateral triangle
        # height = side * sqrt(3) / 2
        height = int(base_length * math.sqrt(3) / 2)
        
        # Calculate the midpoint of the base
        mid_x = (self.start_pos[0] + pos[0]) // 2
        mid_y = (self.start_pos[1] + pos[1]) // 2
        
        # Calculate the third point (apex)
        # We need to find a point perpendicular to the base at distance = height
        # This is simplified - assuming horizontal base for now
        if abs(pos[1] - self.start_pos[1]) < 10:  # Nearly horizontal
            # Third point is above or below the midpoint
            p3 = (mid_x, mid_y - height)
        else:
            # For non-horizontal bases, use perpendicular calculation
            dx = pos[0] - self.start_pos[0]
            dy = pos[1] - self.start_pos[1]
            # Perpendicular vector
            perp_x = -dy
            perp_y = dx
            # Normalize and scale
            length = math.sqrt(perp_x**2 + perp_y**2)
            if length > 0:
                perp_x = (perp_x / length) * height
                perp_y = (perp_y / length) * height
            p3 = (mid_x + perp_x, mid_y + perp_y)
        
        # Draw triangle outline
        pygame.draw.polygon(self.preview_surface, self.color, 
                          [self.start_pos, pos, p3], 2)
    
    def _draw_rhombus_preview(self, pos):
        """
        Draw rhombus (diamond) outline on preview surface
        
        A rhombus has all sides equal but angles can vary.
        We create it using the start and current positions as opposite vertices.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        # Calculate center point
        center_x = (self.start_pos[0] + pos[0]) // 2
        center_y = (self.start_pos[1] + pos[1]) // 2
        
        # Calculate half-width and half-height
        half_width = abs(pos[0] - self.start_pos[0]) // 2
        half_height = abs(pos[1] - self.start_pos[1]) // 2
        
        # Define the four vertices of the rhombus
        # Top vertex
        p1 = (center_x, self.start_pos[1])
        # Right vertex
        p2 = (pos[0], center_y)
        # Bottom vertex
        p3 = (center_x, pos[1])
        # Left vertex
        p4 = (self.start_pos[0], center_y)
        
        # Draw rhombus outline
        pygame.draw.polygon(self.preview_surface, self.color, [p1, p2, p3, p4], 2)
    
    def _draw_brush_or_eraser(self, pos):
        """
        Internal method: Draw brush or eraser stroke
        
        Uses pygame.draw.line to connect points and prevent gaps.
        
        Parameters:
        pos (tuple): Current (x, y) mouse coordinates
        """
        if not self.drawing:
            return
        
        # Draw a line from last position to current position
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
        if self.tool in ["rect", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"]:
            self.canvas.blit(self.preview_surface, (0, 0))
        
        # Reset state
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_surface.fill((0, 0, 0, 0))  # Clean up preview