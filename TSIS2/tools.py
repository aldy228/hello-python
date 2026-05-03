"""
tools.py — Drawing utilities for the Paint application.
This module is imported by paint.py and provides:
  - Shared constants (TOOLBAR_HEIGHT, WHITE)
  - draw_shape(): draws any supported shape onto a pygame Surface
  - flood_fill(): bucket fill algorithm
  - _colors_match(): helper for flood fill color comparison

Keeping these functions in a separate module makes paint.py cleaner
and makes the drawing logic easier to test and modify independently.
"""

import pygame
import math


# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

# TOOLBAR_HEIGHT: how many pixels tall the toolbar area is.
# This is used in both tools.py (canvas size) and paint.py (coordinate conversion).
# Defined here so both files share the same value — change it once, affects both.
TOOLBAR_HEIGHT = 130

# WHITE: the default background/canvas color, used for clearing and erasing.
WHITE = (255, 255, 255)


# ─────────────────────────────────────────────
#  SHAPE DRAWING
# ─────────────────────────────────────────────

def draw_shape(surface, tool_name, color, start_pos, end_pos, brush_size):
    """
    Draw a shape onto the given pygame Surface.

    Called both during live preview (on a temp canvas copy) and on mouse release
    (on the real canvas) — this is why it takes a 'surface' parameter instead of
    drawing directly to a global canvas.

    Parameters:
        surface   (pygame.Surface): the canvas to draw on
        tool_name (str): which shape to draw — one of:
                         "line", "rectangle", "square", "circle",
                         "right triangle", "equilateral", "rhombus"
        color     (tuple): RGB color, e.g. (0, 0, 0) for black
        start_pos (tuple): (x, y) where the drag started (canvas coordinates)
        end_pos   (tuple): (x, y) where the drag ended (canvas coordinates)
        brush_size (int): stroke thickness; if >= 10, shapes are drawn filled (width=0)
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    if tool_name == "line":
        # Simplest case: straight line between two points
        pygame.draw.line(surface, color, start_pos, end_pos, brush_size)

    elif tool_name == "rectangle":
        # Width and height are the difference between start and end
        # Can be negative if the user drags left or up — pygame handles this correctly
        width  = x2 - x1
        height = y2 - y1
        # brush_size < 10 → outline only; brush_size >= 10 → filled (width=0 means filled in pygame)
        pygame.draw.rect(surface, color, (x1, y1, width, height),
                         brush_size if brush_size < 10 else 0)

    elif tool_name == "square":
        # Force equal width and height by using the smaller of the two dimensions
        size = min(abs(x2 - x1), abs(y2 - y1))
        # Preserve dragging direction: if user drags left, size should be negative
        if x2 < x1:
            size = -size
        pygame.draw.rect(surface, color, (x1, y1, size, size),
                         brush_size if brush_size < 10 else 0)

    elif tool_name == "circle":
        # Radius = straight-line distance from start to end (Euclidean distance)
        # math.hypot(dx, dy) = sqrt(dx² + dy²)
        radius = int(math.hypot(x2 - x1, y2 - y1))
        # Center is at start_pos; the user drags outward to set the radius
        pygame.draw.circle(surface, color, start_pos, radius,
                           brush_size if brush_size < 10 else 0)

    elif tool_name == "right triangle":
        # A right triangle with the right angle at start_pos
        # Three vertices: start, directly below start (same x, end's y), end
        #
        #   start_pos ──────── end_pos
        #       |             /
        #       |            /
        #   (x1,y2) ────────
        #
        points = [start_pos, (x1, y2), end_pos]
        pygame.draw.polygon(surface, color, points,
                            brush_size if brush_size < 10 else 0)

    elif tool_name == "equilateral":
        # Equilateral triangle: all three sides equal, all angles 60°
        # Base = line from start_pos to end_pos
        # Apex = third point, offset perpendicular to the base by the triangle's height

        base_len = math.hypot(x2 - x1, y2 - y1)  # length of the base
        height   = base_len * math.sqrt(3) / 2     # height of equilateral triangle

        # Midpoint of the base (apex sits above/beside this point)
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Place the apex perpendicular to the base direction
        # If the base is more horizontal, apex goes up; if more vertical, apex goes right
        if abs(y2 - y1) < abs(x2 - x1):
            apex = (mid_x, mid_y - height)   # apex above midpoint
        else:
            apex = (mid_x + height, mid_y)   # apex to the right of midpoint

        points = [start_pos, end_pos, apex]
        pygame.draw.polygon(surface, color, points,
                            brush_size if brush_size < 10 else 0)

    elif tool_name == "rhombus":
        # Rhombus (diamond shape): start and end are opposite corners of the bounding box
        # The four vertices are at the midpoints of each side of that bounding box
        #
        #         (cx, y1)  ← top
        #        /          \
        #  (x1, cy)        (x2, cy)  ← left and right
        #        \          /
        #         (cx, y2)  ← bottom
        #
        cx = (x1 + x2) // 2  # horizontal center
        cy = (y1 + y2) // 2  # vertical center

        points = [
            (cx, y1),  # top vertex
            (x2, cy),  # right vertex
            (cx, y2),  # bottom vertex
            (x1, cy)   # left vertex
        ]
        pygame.draw.polygon(surface, color, points,
                            brush_size if brush_size < 10 else 0)


# ─────────────────────────────────────────────
#  FLOOD FILL
# ─────────────────────────────────────────────

def flood_fill(surface, start_pos, fill_color, tolerance=0):
    """
    Fill a region of the canvas with fill_color, starting from start_pos.

    This is the classic "paint bucket" tool. It works by:
    1. Noting the color at the clicked pixel (target_color)
    2. Spreading outward to all connected pixels that have the same color
    3. Stopping at pixels that have a different color (the boundary)

    Uses an iterative stack instead of recursion to avoid Python's recursion
    limit crashing the app on large fill areas.

    Parameters:
        surface    (pygame.Surface): canvas to fill
        start_pos  (tuple): (x, y) where the user clicked
        fill_color (tuple): RGB color to fill with, e.g. (255, 0, 0) for red
        tolerance  (int): how different a pixel's color can be and still get filled
                          0 = exact match only (default)
    """
    x, y = start_pos

    width, height = surface.get_size()

    # Guard: don't process clicks outside the canvas bounds
    if not (0 <= x < width and 0 <= y < height):
        return

    # The color we want to replace — [:3] strips the alpha channel if present
    target_color = surface.get_at((x, y))[:3]

    # If the user clicks on a pixel that's already the fill color, do nothing
    # (otherwise the fill would spread across the entire canvas)
    if target_color == fill_color:
        return

    # pygame surfaces use RGBA; we need to set pixels with 4 channels
    fill_rgba = fill_color + (255,)  # fully opaque

    # Stack stores pixels we still need to process
    # We use a stack (LIFO) rather than a queue — the order doesn't matter for fill
    stack = [(x, y)]

    while stack:
        cx, cy = stack.pop()  # take the next pixel to process

        # Check bounds (pixels pushed to stack might be out of bounds)
        if 0 <= cx < width and 0 <= cy < height:
            current_pixel = surface.get_at((cx, cy))[:3]

            # Only fill this pixel if it still matches the original target color
            if _colors_match(current_pixel, target_color, tolerance):
                surface.set_at((cx, cy), fill_rgba)  # paint this pixel

                # Push all 4 neighbors (up, down, left, right) onto the stack
                # We use 4-connectivity (not 8) so fills don't "leak" through corners
                stack.extend([
                    (cx + 1, cy),   # right
                    (cx - 1, cy),   # left
                    (cx,     cy + 1),  # down
                    (cx,     cy - 1)   # up
                ])


def _colors_match(c1, c2, tolerance):
    """
    Check whether two RGB colors are close enough to be considered the same.

    With tolerance=0 (default), both colors must be exactly equal.
    With tolerance>0, each channel (R, G, B) is allowed to differ by up to that amount.
    This is useful for filling areas on anti-aliased edges where pixels aren't
    exactly the same color but are close enough visually.

    Parameters:
        c1, c2    (tuple): RGB tuples, e.g. (255, 0, 0)
        tolerance (int): max allowed difference per channel

    Returns:
        bool: True if the colors match within tolerance
    """
    # zip(c1, c2) pairs up R with R, G with G, B with B
    # all(...) returns True only if every channel difference is within tolerance
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))