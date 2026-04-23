"""
Main Module - Paint Application

This is the main entry point for the Paint app.
It handles:
- Display setup and canvas creation
- Toolbar UI rendering
- Mouse and keyboard event processing
- Tool switching and color selection
- Drawing loop and screen updates
- Cursor preview for brush/eraser sizes
- Save functionality

Application Features:
- Brush, Rectangle, Circle, and Eraser tools
- 8 preset colors
- 4 brush sizes
- Dynamic cursor preview showing tool size
- Keyboard shortcuts for quick tool switching
- Save drawing to PNG file
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
CANVAS_HEIGHT = 750  # Drawing area height
TOOLBAR_HEIGHT = 60  # Height of bottom toolbar
CANVAS_OFFSET_X = 50  # Canvas starts 50px from left
CANVAS_OFFSET_Y = 20  # Canvas starts 20px from top

# Define colors
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
pygame.display.set_caption("Paint")

# Create clock for frame rate control
clock = pygame.time.Clock()

# Create font for toolbar text
font = pygame.font.Font(None, 28)

# ============================================================================
# SURFACES (LAYERS)
# ============================================================================

# 1. The Canvas (Permanent drawings)
# This is a separate surface where all permanent drawings are stored
# Without this, screen.fill() would erase everything each frame
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))

# Fill canvas with white background
canvas.fill(WHITE)

# 2. The Preview Surface (Temporary shapes/ghosts)
# Must have SRCALPHA to allow transparency (clearing it)
# Used for showing shape outlines before they're committed
preview_surface = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)

# ============================================================================
# TOOLS & STATE INITIALIZATION
# ============================================================================

# Create drawing tools instance, pointing to canvas and preview surfaces
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
    """
    Render the bottom toolbar with colors, tools, and options
    
    Layout:
    [Color Palette] [Tool Buttons] [Size Selector]
    """
    # Draw toolbar background rectangle
    # Positioned at bottom of screen
    pygame.draw.rect(screen, GRAY, (0, CANVAS_HEIGHT + CANVAS_OFFSET_Y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
    
    # ----- COLOR PALETTE -----
    x_offset = 20  # Starting x position
    for i, color in enumerate(COLORS):
        # Draw color swatch
        pygame.draw.rect(screen, color, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 40, 40))
        # Draw black border around swatch
        pygame.draw.rect(screen, BLACK, (x_offset, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 40, 40), 2)
        
        # Highlight selected color with white border
        if i == selected_color_index:
            pygame.draw.rect(screen, WHITE, (x_offset - 3, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 7, 46, 46), 3)
        
        # Move to next color position (40px width + 15px gap)
        x_offset += 55
    
    # ----- TOOL BUTTONS -----
    tool_x = 500  # Starting x position for tools
    # List of (button_label, tool_name) tuples
    tools_list = [("Brush", "brush"), ("Rect", "rect"), ("Circle", "circle"), ("Eraser", "eraser")]
    
    for label, tool_name in tools_list:
        # Determine button color: white if selected, gray if not
        btn_color = WHITE if selected_tool == tool_name else GRAY
        
        # Draw tool button
        pygame.draw.rect(screen, btn_color, (tool_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 80, 40))
        pygame.draw.rect(screen, BLACK, (tool_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 80, 40), 2)
        
        # Draw button label
        text = font.render(label, True, BLACK)
        screen.blit(text, (tool_x + 15, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 20))
        
        # Move to next button position
        tool_x += 95
    
    # ----- BRUSH SIZE SELECTOR -----
    size_x = 950
    # Draw size display box
    pygame.draw.rect(screen, WHITE, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 40))
    pygame.draw.rect(screen, BLACK, (size_x, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 10, 150, 40), 2)
    
    # Render current size text
    size_text = font.render(f"Size: {brush_sizes[selected_size_index]}", True, BLACK)
    screen.blit(size_text, (size_x + 15, CANVAS_HEIGHT + CANVAS_OFFSET_Y + 20))

def handle_toolbar_click(pos):
    """
    Process clicks on toolbar elements
    
    Determines which UI element was clicked and updates state accordingly.
    
    Parameters:
    pos (tuple): (x, y) coordinates of mouse click
    
    Returns:
    bool: True if click was on toolbar, False otherwise
    """
    global selected_color_index, selected_tool, selected_size_index
    
    x, y = pos
    
    # Check if click is within toolbar vertical bounds
    if y < CANVAS_HEIGHT + CANVAS_OFFSET_Y or y > CANVAS_HEIGHT + CANVAS_OFFSET_Y + TOOLBAR_HEIGHT:
        return False  # Click was on canvas, not toolbar
    
    # ----- COLOR SELECTION -----
    # Colors occupy x positions 20 to 460 (8 colors * 55px spacing)
    if x < 460:
        index = (x - 20) // 55
        # Validate index is within bounds
        if 0 <= index < len(COLORS):
            selected_color_index = index
            # Update tool color
            tools.set_color(COLORS[index])
            return True
    
    # ----- TOOL SELECTION -----
    # Tools occupy x positions 500 to 900
    if 500 <= x < 900:
        tool_x = 500
        # Check each tool button
        for label, tool_name in [("Brush", "brush"), ("Rect", "rect"), ("Circle", "circle"), ("Eraser", "eraser")]:
            if tool_x <= x < tool_x + 80:
                # Update selected tool
                selected_tool = tool_name
                tools.set_tool(tool_name)
                return True
            tool_x += 95  # Move to next button
    
    # ----- SIZE SELECTION -----
    # Size selector occupies x positions 950 to 1100
    if 950 <= x < 1100:
        # Cycle to next size
        # % len(brush_sizes) wraps around to 0 when reaching end
        selected_size_index = (selected_size_index + 1) % len(brush_sizes)
        tools.set_brush_size(brush_sizes[selected_size_index])
        return True
    
    return False

def get_canvas_coords(mouse_pos):
    """
    Convert screen coordinates to canvas coordinates (removing offset)
    
    The canvas is drawn at (CANVAS_OFFSET_X, CANVAS_OFFSET_Y),
    so we need to subtract this offset to get correct canvas coordinates.
    
    Parameters:
    mouse_pos (tuple): (x, y) screen coordinates
    
    Returns:
    tuple: (x, y) canvas coordinates
    """
    return (mouse_pos[0] - CANVAS_OFFSET_X, mouse_pos[1] - CANVAS_OFFSET_Y)

# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

running = True

while running:
    """
    Main loop for Paint application
    
    Each frame:
    1. Process events (mouse clicks, motion, keyboard)
    2. Handle drawing if mouse is moving while pressed
    3. Render canvas and toolbar to screen
    4. Draw cursor preview
    5. Update display
    """
    
    # -------------------------------------------------------------------------
    # EVENT HANDLING
    # -------------------------------------------------------------------------
    for event in pygame.event.get():
        # Window close button
        if event.type == pygame.QUIT:
            running = False
        
        # Mouse button pressed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                pos = event.pos
                # Check if user clicked on toolbar
                if not handle_toolbar_click(pos):
                    # If not toolbar, start drawing on canvas
                    canvas_pos = get_canvas_coords(pos)
                    tools.start_drawing(canvas_pos)
        
        # Mouse button released
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                canvas_pos = get_canvas_coords(event.pos)
                tools.finish_drawing(canvas_pos)
        
        # Mouse moving
        elif event.type == pygame.MOUSEMOTION:
            if tools.drawing:
                canvas_pos = get_canvas_coords(event.pos)
                # Update preview (for shapes) or draw (for brush)
                if tools.tool in ["rect", "circle"]:
                    tools.update_preview(canvas_pos)
                else:
                    tools.draw(canvas_pos)
        
        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            # Quick tool switching without using toolbar
            if event.key == pygame.K_b:
                selected_tool = "brush"
                tools.set_tool("brush")
            elif event.key == pygame.K_r:
                selected_tool = "rect"
                tools.set_tool("rect")
            elif event.key == pygame.K_c:
                selected_tool = "circle"
                tools.set_tool("circle")
            elif event.key == pygame.K_e:
                selected_tool = "eraser"
                tools.set_tool("eraser")
            elif event.key == pygame.K_s:
                # Save current canvas to file
                # pygame.image.save() exports surface to image file
                pygame.image.save(canvas, "painting.png")
                print("✅ Drawing saved as painting.png")
    
    # -------------------------------------------------------------------------
    # RENDERING
    # -------------------------------------------------------------------------
    
    # Clear main screen
    screen.fill(WHITE)
    
    # Draw canvas at offset position
    # This creates margins around the drawing area
    screen.blit(canvas, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw preview (ghost shapes) ON TOP of canvas
    screen.blit(preview_surface, (CANVAS_OFFSET_X, CANVAS_OFFSET_Y))
    
    # Draw toolbar at bottom
    draw_toolbar()
    
    # -------------------------------------------------------------------------
    # CURSOR PREVIEW (Dynamic tool size indicator)
    # -------------------------------------------------------------------------
    
    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Check if mouse is inside the canvas area
    if (CANVAS_OFFSET_X <= mouse_pos[0] < CANVAS_OFFSET_X + CANVAS_WIDTH and
        CANVAS_OFFSET_Y <= mouse_pos[1] < CANVAS_OFFSET_Y + CANVAS_HEIGHT):
        
        # Determine preview size and color based on active tool
        if tools.tool == "eraser":
            # Eraser size is doubled in logic, so we double it for preview
            radius = tools.brush_size * 2
            color = (255, 0, 0)  # Red outline for eraser (high contrast)
        elif tools.tool == "brush":
            radius = tools.brush_size
            color = tools.color  # Brush uses selected color
        else:
            radius = 0  # No preview for shapes
        
        if radius > 0:
            # Draw circle outline at mouse position
            # width=1 makes a thin outline
            pygame.draw.circle(screen, color, mouse_pos, radius, 1)
            # Draw center dot for precision aiming
            pygame.draw.circle(screen, color, mouse_pos, 2)
    
    # -------------------------------------------------------------------------
    # DISPLAY UPDATE
    # -------------------------------------------------------------------------
    
    # Update display to show new frame
    pygame.display.flip()
    
    # Maintain 60 FPS for smooth drawing
    clock.tick(60)

# ============================================================================
# CLEANUP
# ============================================================================

pygame.quit()
sys.exit()