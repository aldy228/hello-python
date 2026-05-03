"""
Main Module - Paint Application (Practice 11)

Updated with new shape tools:
- Square
- Right Triangle
- Equilateral Triangle
- Rhombus
"""

import pygame  # Import pygame library
import sys  # Import sys for program exit
from tools import DrawingTools  # Import drawing tools class

# ============================================================================
# INITIALIZATION
# ============================================================================

pygame.init()  # Initialize pygame modules

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

SCREEN_WIDTH = 1200  # Total window width
SCREEN_HEIGHT = 900  # Total window height
CANVAS_WIDTH = 1100  # Drawing area width
CANVAS_HEIGHT = 700  # Drawing area height (reduced for toolbar space)
TOOLBAR_HEIGHT = 80  # Height of bottom toolbar (increased for more tools)
CANVAS_OFFSET_X = 50  # Canvas starts 50px from left
CANVAS_OFFSET_Y = 20  # Canvas starts 20px from top

# Colors
WHITE = (255, 255, 255)  # Background and eraser color
BLACK = (0, 0, 0)  # Text and default drawing color
GRAY = (220, 220, 220)  # Toolbar background

# Color palette: 8 preset colors for user selection
COLORS = [
    (0, 0, 0),      # Black
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta/Purple
    (0, 255, 255),  # Cyan/Light Blue
    (255, 165, 0),  # Orange
]

# ============================================================================
# DISPLAY & FONT SETUP
# ============================================================================

# Create main display surface
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint - Practice 11")

# Create clock for frame rate control
clock = pygame.time.Clock()

# Create font for toolbar text
font = pygame.font.Font(None, 24)

# ============================================================================
# SURFACES (LAYERS)
# ============================================================================

# 1. The Canvas (Permanent drawings)
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)

# 2. The Preview Surface (Temporary shapes/ghosts)
preview_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)

# ============================================================================
# TOOLS & STATE INITIALIZATION
# ============================================================================

# Create drawing tools instance
tools = DrawingTools(canvas, preview_surface)

# UI state variables
selected_color_index = 0  # Currently selected color (index in COLORS list)
selected_tool = "brush"   # Currently active tool
brush_sizes = [5, 10, 20, 40]  # Available brush sizes
selected_size_index = 1  # Currently selected size (index in brush_sizes)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def draw_toolbar():
    """Draw the bottom toolbar with all tools"""
    # Toolbar background
    pygame.draw.rect(screen, GRAY, (0, CANVAS_HEIGHT + CANVAS_OFFSET_Y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
    
    # Color Palette (left side)
    x_offset = 10
    for i, color in enumerate(COLORS):
        pygame.draw.rect(screen, color, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 35, 35))
        pygame.draw.rect(screen, BLACK, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 35, 35), 2)
        if i == selected_color_index:
            pygame.draw.rect(screen, WHITE, (x_offset - 2, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 8, 39, 39), 2)
        x_offset += 42
    
    # Tool Buttons (center) - TWO ROWS for all tools
    tool_x = 380
    tool_y = CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10
    
    # First row of tools
    tools_row1 = [
        ("Brush", "brush"), 
        ("Rect", "rect"), 
        ("Square", "square"),
        ("R-Tri", "right_triangle")
    ]
    
    for label, tool_name in tools_row1:
        btn_color = WHITE if selected_tool == tool_name else (180, 180, 180)
        pygame.draw.rect(screen, btn_color, (tool_x, tool_y, 70, 30))
        pygame.draw.rect(screen, BLACK, (tool_x, tool_y, 70, 30), 2)
        text = font.render(label, True, BLACK)
        screen.blit(text, (tool_x + 10, tool_y + 8))
        tool_x += 78
    
    # Second row of tools
    tool_x = 380
    tool_y = CANVAS_HEIGHT + CANVAS_OFFSET_Y + 45
    
    tools_row2 = [
        ("E-Tri", "equilateral_triangle"), 
        ("Rhombus", "rhombus"),
        ("Circle", "circle"), 
        ("Eraser", "eraser")
    ]
    
    for label, tool_name in tools_row2:
        btn_color = WHITE if selected_tool == tool_name else (180, 180, 180)
        pygame.draw.rect(screen, btn_color, (tool_x, tool_y, 70, 30))
        pygame.draw.rect(screen, BLACK, (tool_x, tool_y, 70, 30), 2)
        text = font.render(label, True, BLACK)
        screen.blit(text, (tool_x + 10, tool_y + 8))
        tool_x += 78
    
    # Size Selector (right side)
    size_x = 1000
    pygame.draw.rect(screen, WHITE, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 30))
    pygame.draw.rect(screen, BLACK, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 30), 2)
    size_text = font.render(f"Size: {brush_sizes[selected_size_index]}", True, BLACK)
    screen.blit(size_text, (size_x + 10, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 18))

def handle_toolbar_click(pos):
    """Handle clicks on the toolbar"""
    global selected_color_index, selected_tool, selected_size_index
    
    x, y = pos
    
    # Check if click is within toolbar vertical bounds
    if y < CANVAS_HEIGHT + CANVAS_OFFSET_Y or y > CANVAS_HEIGHT + CANVAS_OFFSET_Y + TOOLBAR_HEIGHT:
        return False
    
    # Color Selection (left side)
    if x < 360:
        index = (x - 10) // 42
        if 0 <= index < len(COLORS):
            selected_color_index = index
            tools.set_color(COLORS[index])
            return True
    
    # Tool Buttons (center) - Check both rows
    tool_y1 = CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10
    tool_y2 = CANVAS_HEIGHT + CANVAS_OFFSET_Y + 45
    
    # First row
    if tool_y1 <= y <= tool_y1 + 30:
        tool_x = 380
        tools_row1 = [("Brush", "brush"), ("Rect", "rect"), ("Square", "square"), ("R-Tri", "right_triangle")]
        for label, tool_name in tools_row1:
            if tool_x <= x < tool_x + 70:
                selected_tool = tool_name
                tools.set_tool(tool_name)
                return True
            tool_x += 78
    
    # Second row
    if tool_y2 <= y <= tool_y2 + 30:
        tool_x = 380
        tools_row2 = [("E-Tri", "equilateral_triangle"), ("Rhombus", "rhombus"), ("Circle", "circle"), ("Eraser", "eraser")]
        for label, tool_name in tools_row2:
            if tool_x <= x < tool_x + 70:
                selected_tool = tool_name
                tools.set_tool(tool_name)
                return True
            tool_x += 78
    
    # Size Selector (right side)
    if 1000 <= x < 1150 and CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10 <= y <= CANVAS_HEIGHT + CANVAS_OFFSET_Y + 40:
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
            if event.button == 1:  # Left mouse button
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
                if tools.tool in ["rect", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"]:
                    tools.update_preview(canvas_pos)
                else:
                    tools._draw_brush_or_eraser(canvas_pos)
        
        elif event.type == pygame.KEYDOWN:
            # Keyboard shortcuts for tools
            if event.key == pygame.K_b:
                selected_tool = "brush"
                tools.set_tool("brush")
            elif event.key == pygame.K_r:
                selected_tool = "rect"
                tools.set_tool("rect")
            elif event.key == pygame.K_s:
                selected_tool = "square"
                tools.set_tool("square")
            elif event.key == pygame.K_c:
                selected_tool = "circle"
                tools.set_tool("circle")
            elif event.key == pygame.K_e:
                selected_tool = "eraser"
                tools.set_tool("eraser")
            elif event.key == pygame.K_t:
                selected_tool = "right_triangle"
                tools.set_tool("right_triangle")
            elif event.key == pygame.K_w:  # Save
                pygame.image.save(canvas, "painting.png")
                print("✅ Drawing saved as painting.png")

    # 2. Rendering
    screen.fill(WHITE)
    
    # Draw canvas at offset position
    screen.blit(canvas, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw preview (ghost shapes) ON TOP of canvas
    screen.blit(preview_surface, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw toolbar at bottom
    draw_toolbar()
    
    # 3. Cursor Preview (Dynamic tool size indicator)
    mouse_pos = pygame.mouse.get_pos()
    
    # Check if mouse is inside the canvas area
    if (CANVAS_OFFSET_X <= mouse_pos[0] < CANVAS_OFFSET_X + CANVAS_WIDTH and
        CANVAS_OFFSET_Y <= mouse_pos[1] < CANVAS_OFFSET_Y + CANVAS_HEIGHT):
        
        # Determine preview size and color based on active tool
        if tools.tool == "eraser":
            radius = tools.brush_size * 2
            color = (255, 0, 0)  # Red outline for eraser
        elif tools.tool == "brush":
            radius = tools.brush_size
            color = tools.color
        else:
            radius = 0
        
        if radius > 0:
            pygame.draw.circle(screen, color, mouse_pos, radius, 1)
            pygame.draw.circle(screen, color, mouse_pos, 2)
    
    # Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()