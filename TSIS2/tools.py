"""
Tools Module - Drawing Functions for Paint App

This module provides standalone functions for:
- Drawing shapes (line, rect, circle, triangle, rhombus)
- Flood-fill algorithm
- Constants shared with main app

Designed to work with paint.py's functional architecture.
"""

import pygame
import math

# ============================================================================
# CONSTANTS (Exported for paint.py)
# ============================================================================

TOOLBAR_HEIGHT = 130  # Height of toolbar area at top
WHITE = (255, 255, 255)  # Default canvas/background color

# ============================================================================
# SHAPE DRAWING FUNCTION
# ============================================================================

def draw_shape(surface, tool_name, color, start_pos, end_pos, brush_size):
    """
    Draw a shape on the given surface
    
    Parameters:
    surface (pygame.Surface): Canvas to draw on
    tool_name (str): One of "line", "rectangle", "circle", "square", 
                     "right triangle", "equilateral", "rhombus"
    color (tuple): RGB color tuple
    start_pos (tuple): (x, y) starting position
    end_pos (tuple): (x, y) ending position
    brush_size (int): Stroke thickness (0 = filled shape)
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    if tool_name == "line":
        # Straight line between two points
        pygame.draw.line(surface, color, start_pos, end_pos, brush_size)
    
    elif tool_name == "rectangle":
        # Rectangle from start to end (can be any dimensions)
        width = x2 - x1
        height = y2 - y1
        # width=brush_size for outline, 0 for filled
        pygame.draw.rect(surface, color, (x1, y1, width, height), 
                        brush_size if brush_size < 10 else 0)
    
    elif tool_name == "square":
        # Square: use smaller dimension to ensure equal sides
        size = min(abs(x2 - x1), abs(y2 - y1))
        # Preserve direction (negative for left/up drawing)
        if x2 < x1:
            size = -size
        pygame.draw.rect(surface, color, (x1, y1, size, size),
                        brush_size if brush_size < 10 else 0)
    
    elif tool_name == "circle":
        # Circle: radius = distance from start to end
        radius = int(math.hypot(x2 - x1, y2 - y1))
        # width=brush_size for outline, 0 for filled
        pygame.draw.circle(surface, color, start_pos, radius,
                          brush_size if brush_size < 10 else 0)
    
    elif tool_name == "right triangle":
        # Right triangle: right angle at start_pos
        # Points: start, (start.x, end.y), end
        points = [start_pos, (x1, y2), end_pos]
        pygame.draw.polygon(surface, color, points,
                           brush_size if brush_size < 10 else 0)
    
    elif tool_name == "equilateral":
        # Equilateral triangle: all sides equal, all angles 60°
        base_len = math.hypot(x2 - x1, y2 - y1)
        height = base_len * math.sqrt(3) / 2
        
        # Midpoint of base
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Calculate apex (third point) perpendicular to base
        # Simplified: assume mostly horizontal base
        if abs(y2 - y1) < abs(x2 - x1):  # Horizontal-ish
            apex = (mid_x, mid_y - height)
        else:  # Vertical-ish
            apex = (mid_x + height, mid_y)
        
        points = [start_pos, end_pos, apex]
        pygame.draw.polygon(surface, color, points,
                           brush_size if brush_size < 10 else 0)
    
    elif tool_name == "rhombus":
        # Rhombus: diamond shape with start/end as opposite vertices
        cx = (x1 + x2) // 2  # Center x
        cy = (y1 + y2) // 2  # Center y
        
        # Four vertices: top, right, bottom, left
        points = [
            (cx, y1),  # Top
            (x2, cy),  # Right
            (cx, y2),  # Bottom
            (x1, cy)   # Left
        ]
        pygame.draw.polygon(surface, color, points,
                           brush_size if brush_size < 10 else 0)

# ============================================================================
# FLOOD FILL ALGORITHM
# ============================================================================

def flood_fill(surface, start_pos, fill_color, tolerance=0):
    """
    Stack-based flood fill algorithm
    
    Fills connected region of target_color with fill_color.
    Stops at boundaries of different colors.
    
    Parameters:
    surface (pygame.Surface): Canvas to fill
    start_pos (tuple): (x, y) starting position for fill
    fill_color (tuple): RGB color to fill with
    tolerance (int): Color matching tolerance (0 = exact match)
    """
    x, y = start_pos
    
    # Boundary check
    width, height = surface.get_size()
    if not (0 <= x < width and 0 <= y < height):
        return
    
    # Get target color at click position (RGB only, ignore alpha)
    target_color = surface.get_at((x, y))[:3]
    
    # Don't fill if target and fill colors match
    if target_color == fill_color:
        return
    
    # Prepare fill color with alpha channel
    fill_rgba = fill_color + (255,)
    
    # Stack for iterative flood fill (avoids recursion limit)
    stack = [(x, y)]
    
    while stack:
        cx, cy = stack.pop()
        
        # Boundary check
        if 0 <= cx < width and 0 <= cy < height:
            current_pixel = surface.get_at((cx, cy))[:3]
            
            # If pixel matches target color (within tolerance), fill it
            if _colors_match(current_pixel, target_color, tolerance):
                surface.set_at((cx, cy), fill_rgba)
                
                # Add 4-connected neighbors to stack
                stack.extend([
                    (cx + 1, cy),  # Right
                    (cx - 1, cy),  # Left
                    (cx, cy + 1),  # Down
                    (cx, cy - 1)   # Up
                ])

def _colors_match(c1, c2, tolerance):
    """
    Check if two RGB colors match within tolerance
    
    Parameters:
    c1, c2 (tuple): RGB color tuples (R, G, B)
    tolerance (int): Max difference per channel (0 = exact)
    
    Returns:
    bool: True if colors match within tolerance
    """
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))