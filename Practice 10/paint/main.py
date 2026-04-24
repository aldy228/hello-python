"""
Main Module - Paint Application (Final Polish)

Added:
- Dynamic cursor preview for Brush and Eraser sizes
- Improved visual feedback for tool selection
"""

import pygame
import sys
from tools import DrawingTools

# ============================================================================
# INITIALIZATION
# ============================================================================

pygame.init()

# Constants - Optimized size for better workflow
SCREEN_WIDTH = 1200  
SCREEN_HEIGHT = 900
CANVAS_WIDTH = 1100
CANVAS_HEIGHT = 750
TOOLBAR_HEIGHT = 60
CANVAS_OFFSET_X = 50
CANVAS_OFFSET_Y = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
COLORS = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 165, 0)
]

# Display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# Surfaces
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)

preview_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)

# Tools
tools = DrawingTools(canvas, preview_surface)

# UI State
selected_color_index = 0
selected_tool = "brush"
brush_sizes = [5, 10, 20, 40]
selected_size_index = 1

def draw_toolbar():
    """Draw the bottom toolbar"""
    # Background
    pygame.draw.rect(screen, GRAY, (0, CANVAS_HEIGHT + CANVAS_OFFSET_Y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
    
    # Colors
    x_offset = 20
    for i, color in enumerate(COLORS):
        pygame.draw.rect(screen, color, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 40, 40))
        pygame.draw.rect(screen, BLACK, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 40, 40), 2)
        # Highlight selected
        if i == selected_color_index:
            pygame.draw.rect(screen, WHITE, (x_offset - 3, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 7, 46, 46), 3)
        x_offset += 55
        
    # Tools
    tool_x = 500
    tools_list = [("Brush", "brush"), ("Rect", "rect"), ("Circle", "circle"), ("Eraser", "eraser")]
    for label, tool_name in tools_list:
        btn_color = WHITE if selected_tool == tool_name else GRAY
        pygame.draw.rect(screen, btn_color, (tool_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 80, 40))
        pygame.draw.rect(screen, BLACK, (tool_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 80, 40), 2)
        text = font.render(label, True, BLACK)
        screen.blit(text, (tool_x + 15, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 20))
        tool_x += 95
        
    # Size
    size_x = 950
    pygame.draw.rect(screen, WHITE, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 40))
    pygame.draw.rect(screen, BLACK, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 40), 2)
    size_text = font.render(f"Size: {brush_sizes[selected_size_index]}", True, BLACK)
    screen.blit(size_text, (size_x + 15, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 20))

def handle_toolbar_click(pos):
    """Handle clicks on the toolbar"""
    global selected_color_index, selected_tool, selected_size_index
    x, y = pos
    
    if y < CANVAS_HEIGHT + CANVAS_OFFSET_Y or y > CANVAS_HEIGHT + CANVAS_OFFSET_Y + TOOLBAR_HEIGHT:
        return False
    
    # Colors
    if x < 460:
        index = (x - 20) // 55
        if 0 <= index < len(COLORS):
            selected_color_index = index
            tools.set_color(COLORS[index])
            return True
            
    # Tools
    if 500 <= x < 900:
        tool_x = 500
        for label, tool_name in [("Brush", "brush"), ("Rect", "rect"), ("Circle", "circle"), ("Eraser", "eraser")]:
            if tool_x <= x < tool_x + 80:
                selected_tool = tool_name
                tools.set_tool(tool_name)
                return True
            tool_x += 95
            
    # Size
    if 950 <= x < 1100:
        selected_size_index = (selected_size_index + 1) % len(brush_sizes)
        tools.set_brush_size(brush_sizes[selected_size_index])
        return True
    return False

def get_canvas_coords(mouse_pos):
    """Convert screen coordinates to canvas coordinates"""
    return (mouse_pos[0] - CANVAS_OFFSET_X, mouse_pos[1] - CANVAS_OFFSET_Y)

# ============================================================================
# MAIN LOOP
# ============================================================================

running = True

while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not handle_toolbar_click(event.pos):
                    canvas_pos = get_canvas_coords(event.pos)
                    tools.start_drawing(canvas_pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                canvas_pos = get_canvas_coords(event.pos)
                tools.finish_drawing(canvas_pos)
        
        elif event.type == pygame.MOUSEMOTION:
            if tools.drawing:
                canvas_pos = get_canvas_coords(event.pos)
                if tools.tool in ["rect", "circle"]:
                    tools.update_preview(canvas_pos)
                else:
                    tools.draw(canvas_pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b: selected_tool = "brush"; tools.set_tool("brush")
            elif event.key == pygame.K_r: selected_tool = "rect"; tools.set_tool("rect")
            elif event.key == pygame.K_c: selected_tool = "circle"; tools.set_tool("circle")
            elif event.key == pygame.K_e: selected_tool = "eraser"; tools.set_tool("eraser")
            elif event.key == pygame.K_s:
                pygame.image.save(canvas, "painting.png")
                print("Saved!")

    # 2. Rendering
    screen.fill(WHITE)
    
    # Draw Canvas
    screen.blit(canvas, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw Preview (Ghost shapes)
    screen.blit(preview_surface, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw Toolbar
    draw_toolbar()

    # 3. NEW: Draw Cursor Preview (Dynamic Tool Size)
    mouse_pos = pygame.mouse.get_pos()
    # Check if mouse is inside the canvas area
    if (CANVAS_OFFSET_X <= mouse_pos[0] < CANVAS_OFFSET_X + CANVAS_WIDTH and
        CANVAS_OFFSET_Y <= mouse_pos[1] < CANVAS_OFFSET_Y + CANVAS_HEIGHT):
        
        # Determine preview size and color based on active tool
        if tools.tool == "eraser":
            # Eraser size is doubled in logic, so we double it for preview
            radius = tools.brush_size * 2
            color = (255, 0, 0)  # Red outline for eraser
        elif tools.tool == "brush":
            radius = tools.brush_size
            color = tools.color  # Brush uses selected color
        else:
            radius = 0 # No preview for shapes
            
        if radius > 0:
            # Draw circle outline at mouse position
            pygame.draw.circle(screen, color, mouse_pos, radius, 1)
            # Draw center dot for precision
            pygame.draw.circle(screen, color, mouse_pos, 2)

    # Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 