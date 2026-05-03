"""
paint.py — Main file for the Paint application (TSIS 2).
Handles the game loop, toolbar rendering, user input, and drawing logic.
Uses pygame for graphics and imports shape/fill utilities from tools.py.
"""

import pygame
import os
from datetime import datetime
from tools import TOOLBAR_HEIGHT, WHITE, draw_shape, flood_fill
# TOOLBAR_HEIGHT and WHITE are constants defined in tools.py
# draw_shape handles all shape drawing (line, rect, circle, etc.)
# flood_fill handles the bucket fill tool

pygame.init()  # must be called before using any pygame features

# ─────────────────────────────────────────────
#  WINDOW SETUP
# ─────────────────────────────────────────────

WIDTH = 900
HEIGHT = 600
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT  # drawing area = full height minus the toolbar

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # create the window
pygame.display.set_caption("Paint application TSIS 2")

# ─────────────────────────────────────────────
#  ASSET PATHS
# ─────────────────────────────────────────────

# BASE_DIR = the folder where this script lives (used to find assets and save paintings)
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")  # folder containing icon images

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────

BLACK  = (0,   0,   0)
RED    = (230, 70,  70)
GREEN  = (70,  180, 90)
BLUE   = (70,  120, 230)
YELLOW = (240, 210, 70)
PURPLE = (160, 90,  200)

LIGHT_GRAY = (245, 247, 250)  # toolbar background
GRAY       = (220, 225, 235)  # toolbar border line
DARK_GRAY  = (70,  70,  80)   # button borders and help text

# ─────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────

font      = pygame.font.SysFont("Arial", 16)  # used for toolbar labels
text_font = pygame.font.SysFont("Arial", 28)  # used for the text tool on canvas

# ─────────────────────────────────────────────
#  CANVAS SETUP
# ─────────────────────────────────────────────

# The canvas is a separate Surface — only this area is saved when exporting.
# It doesn't include the toolbar, so saved images are clean drawings only.
canvas = pygame.Surface((WIDTH, CANVAS_HEIGHT))
canvas.fill(WHITE)  # start with a blank white canvas

# ─────────────────────────────────────────────
#  APP STATE
# ─────────────────────────────────────────────

current_tool  = "brush"  # which tool is active
current_color = BLACK    # current drawing color
brush_size    = 5        # stroke thickness in pixels

# Drawing state — used to track mouse drag for shapes and freehand drawing
drawing   = False     # True while the mouse button is held down
start_pos = None      # canvas position where the drag started
last_pos  = None      # last known canvas position (used for smooth brush strokes)

# Text tool state
typing     = False    # True while the user is typing text on canvas
text_pos   = None     # canvas position where text will be placed
typed_text = ""       # accumulates characters as the user types


# ─────────────────────────────────────────────
#  ICON LOADING
# ─────────────────────────────────────────────

def load_icon(filename):
    """
    Load an icon image from the assets folder and scale it to 22x22 pixels.
    Returns None if the file is missing — the toolbar will draw a fallback icon instead.
    convert_alpha() optimizes the image for fast blitting with transparency.
    """
    try:
        path = os.path.join(ASSETS_DIR, filename)
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (22, 22))
    except (FileNotFoundError, pygame.error) as e:
        print(f"⚠️ Warning: Could not load {filename}: {e}")
        print(f"   Using fallback icon instead")
        return None  # None signals draw_icon_with_pygame() to use a pygame fallback


# Load icons for tools that have image assets; others use pygame-drawn fallbacks
asset_icons = {
    "brush":  load_icon("brush.png"),
    "eraser": load_icon("eraser.png"),
    "fill":   load_icon("fill.png"),
    "line":   load_icon("line.png")
}


# ─────────────────────────────────────────────
#  TOOLBAR LAYOUT
# ─────────────────────────────────────────────

# Each tool_button is a pygame.Rect defining its clickable area on screen
# Rect(x, y, width, height) — all positions are in screen coordinates
tool_buttons = {
    "brush":          pygame.Rect(10,  10, 90,  32),
    "line":           pygame.Rect(110, 10, 80,  32),
    "eraser":         pygame.Rect(200, 10, 90,  32),
    "fill":           pygame.Rect(300, 10, 80,  32),
    "text":           pygame.Rect(390, 10, 80,  32),
    "clear":          pygame.Rect(480, 10, 80,  32),
    "rectangle":      pygame.Rect(570, 10, 115, 32),
    "circle":         pygame.Rect(695, 10, 90,  32),
    "square":         pygame.Rect(795, 10, 90,  32),

    "right triangle": pygame.Rect(10,  52, 130, 32),
    "equilateral":    pygame.Rect(150, 52, 120, 32),
    "rhombus":        pygame.Rect(280, 52, 110, 32)
}

# color_buttons: list of (color, Rect) — each is a clickable color swatch
color_buttons = [
    (BLACK,  pygame.Rect(10,  95, 32, 32)),
    (RED,    pygame.Rect(50,  95, 32, 32)),
    (GREEN,  pygame.Rect(90,  95, 32, 32)),
    (BLUE,   pygame.Rect(130, 95, 32, 32)),
    (YELLOW, pygame.Rect(170, 95, 32, 32)),
    (PURPLE, pygame.Rect(210, 95, 32, 32))
]

# size_buttons: map from pixel size → clickable Rect
size_buttons = {
    2:  pygame.Rect(270, 95, 65, 32),
    5:  pygame.Rect(345, 95, 65, 32),
    10: pygame.Rect(420, 95, 70, 32)
}


# ─────────────────────────────────────────────
#  COORDINATE HELPERS
# ─────────────────────────────────────────────

def screen_to_canvas(pos):
    """
    Convert a screen position to a canvas position.
    The canvas starts at y=TOOLBAR_HEIGHT on screen, so we subtract that offset.
    This ensures drawing coordinates are relative to the canvas, not the window.
    """
    return (pos[0], pos[1] - TOOLBAR_HEIGHT)


def is_on_canvas(pos):
    """
    Check whether a screen position is inside the drawing area (below the toolbar).
    Prevents accidental drawing when clicking toolbar buttons.
    """
    return pos[1] >= TOOLBAR_HEIGHT


# ─────────────────────────────────────────────
#  SAVE / CLEAR
# ─────────────────────────────────────────────

def save_canvas():
    """
    Save the current canvas (drawing area only) as a PNG file.
    Files are saved in a 'paintings/' subfolder with a timestamp in the filename
    so each save creates a new file rather than overwriting the previous one.
    The toolbar is NOT included in the saved image — only the drawing area.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    paintings_folder = os.path.join(BASE_DIR, "paintings")

    # Create the folder if it doesn't exist yet
    if not os.path.exists(paintings_folder):
        os.makedirs(paintings_folder)

    filename = f"paint_{timestamp}.png"
    filepath = os.path.join(paintings_folder, filename)

    # pygame.image.save() writes the Surface to disk as a PNG
    pygame.image.save(canvas, filepath)
    print("Saved:", filepath)


def clear_canvas():
    """
    Fill the entire canvas with white, erasing all drawings.
    This does not affect the toolbar or saved files.
    """
    canvas.fill(WHITE)
    print("Canvas cleared")


# ─────────────────────────────────────────────
#  ICON DRAWING
# ─────────────────────────────────────────────

def draw_icon_with_pygame(tool, rect):
    """
    Draw a small icon inside a toolbar button.
    If a PNG icon was loaded for this tool, blit it onto the screen.
    Otherwise, draw a simple geometric fallback using pygame.draw functions.
    This approach means the app works even if icon files are missing.
    """
    # Use loaded PNG icon if available
    if tool in asset_icons and asset_icons[tool] is not None:
        screen.blit(asset_icons[tool], (rect.x + 5, rect.y + 5))
        return

    # Fallback: draw a simple representative shape using pygame primitives
    x = rect.x + 6
    y = rect.y + 6

    if tool == "text":
        # Draw a capital T shape to represent text input
        pygame.draw.line(screen, BLACK, (x + 2,  y),      (x + 18, y),      2)  # horizontal bar
        pygame.draw.line(screen, BLACK, (x + 10, y),      (x + 10, y + 20), 2)  # vertical bar

    elif tool == "clear":
        # Draw an X to represent clearing/deleting
        pygame.draw.line(screen, BLACK, (x + 3,  y + 3),  (x + 18, y + 18), 3)
        pygame.draw.line(screen, BLACK, (x + 18, y + 3),  (x + 3,  y + 18), 3)

    elif tool == "rectangle":
        pygame.draw.rect(screen, BLACK, (x, y + 4, 20, 13), 2)

    elif tool == "circle":
        pygame.draw.circle(screen, BLACK, (x + 11, y + 11), 9, 2)

    elif tool == "square":
        pygame.draw.rect(screen, BLACK, (x + 3, y + 3, 16, 16), 2)

    elif tool == "right triangle":
        # Right angle at top-left
        points = [(x + 2, y + 2), (x + 2, y + 20), (x + 20, y + 20)]
        pygame.draw.polygon(screen, BLACK, points, 2)

    elif tool == "equilateral":
        # Triangle with apex at top-center
        points = [(x + 11, y + 2), (x + 2, y + 20), (x + 20, y + 20)]
        pygame.draw.polygon(screen, BLACK, points, 2)

    elif tool == "rhombus":
        # Diamond shape: 4 points at top/right/bottom/left
        points = [(x + 11, y + 2), (x + 20, y + 11), (x + 11, y + 20), (x + 2, y + 11)]
        pygame.draw.polygon(screen, BLACK, points, 2)


# ─────────────────────────────────────────────
#  TOOLBAR RENDERING
# ─────────────────────────────────────────────

def draw_toolbar():
    """
    Render the entire toolbar area at the top of the window.
    Draws three rows:
      Row 1 (y=10): main tool buttons (brush, line, eraser, fill, text, clear, shapes)
      Row 2 (y=52): extra shape buttons (right triangle, equilateral, rhombus)
      Row 3 (y=95): color swatches and brush size buttons
    The active tool and color are highlighted in blue.
    """
    # Toolbar background
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    # Bottom border line separating toolbar from canvas
    pygame.draw.line(screen, GRAY, (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

    # ── Tool buttons ──
    for tool, rect in tool_buttons.items():
        # Highlight the active tool in blue; others are white
        if tool == current_tool:
            button_color = BLUE
            text_color   = WHITE
        else:
            button_color = WHITE
            text_color   = BLACK

        pygame.draw.rect(screen, button_color, rect, border_radius=8)   # filled background
        pygame.draw.rect(screen, DARK_GRAY,    rect, 1, border_radius=8)  # border outline

        draw_icon_with_pygame(tool, rect)  # icon on the left side of the button

        # Tool name label to the right of the icon
        label = font.render(tool, True, text_color)
        screen.blit(label, (rect.x + 32, rect.y + 8))

    # ── Color swatches ──
    for color, rect in color_buttons:
        pygame.draw.rect(screen, color, rect, border_radius=8)  # filled with the color

        # Highlight active color with a thick blue border
        if color == current_color:
            pygame.draw.rect(screen, BLUE,      rect, 4, border_radius=8)
        else:
            pygame.draw.rect(screen, DARK_GRAY, rect, 1, border_radius=8)

    # ── Brush size buttons ──
    for size, rect in size_buttons.items():
        if size == brush_size:
            button_color = BLUE
            text_color   = WHITE
        else:
            button_color = WHITE
            text_color   = BLACK

        pygame.draw.rect(screen, button_color, rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GRAY,    rect, 1, border_radius=8)

        label = font.render(str(size) + " px", True, text_color)
        screen.blit(label, (rect.x + 10, rect.y + 8))

    # Keyboard shortcut hint displayed in the toolbar
    help_text = "1 small | 2 medium | 3 large | Ctrl+S save"
    label = font.render(help_text, True, DARK_GRAY)
    screen.blit(label, (510, 102))


# ─────────────────────────────────────────────
#  MAIN GAME LOOP
# ─────────────────────────────────────────────

running = True
clock = pygame.time.Clock()  # used to cap the frame rate at 60 FPS

while running:

    # 1. Clear the screen and draw the canvas
    screen.fill(WHITE)
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))  # draw canvas below the toolbar

    # 2. Live preview — show shapes while dragging before mouse button is released
    # Only applies to tools that draw by dragging (not brush/eraser/fill)
    if drawing and start_pos is not None and current_tool in [
        "line", "rectangle", "circle", "square",
        "right triangle", "equilateral", "rhombus"
    ]:
        # Work on a temporary copy so the preview doesn't permanently mark the canvas
        temp = canvas.copy()
        mouse_pos = pygame.mouse.get_pos()

        if is_on_canvas(mouse_pos):
            end_pos = screen_to_canvas(mouse_pos)
            draw_shape(temp, current_tool, current_color, start_pos, end_pos, brush_size)

        screen.blit(temp, (0, TOOLBAR_HEIGHT))  # show the preview

    # 3. Live text preview — show what the user is typing before they press Enter
    if typing and text_pos is not None:
        text_surface = text_font.render(typed_text, True, current_color)
        # text_pos is in canvas coords, so add TOOLBAR_HEIGHT to get screen coords
        screen.blit(text_surface, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    # 4. Draw the toolbar on top of everything
    draw_toolbar()

    # 5. Handle all events (keyboard, mouse, window close)
    for event in pygame.event.get():

        # ── Window close button ──
        if event.type == pygame.QUIT:
            running = False

        # ── Keyboard input ──
        elif event.type == pygame.KEYDOWN:

            if typing:
                # Text tool is active — route all keys to text input
                if event.key == pygame.K_RETURN:
                    # Commit the typed text to the canvas permanently
                    text_surface = text_font.render(typed_text, True, current_color)
                    canvas.blit(text_surface, text_pos)
                    typing = False
                    text_pos = None
                    typed_text = ""

                elif event.key == pygame.K_ESCAPE:
                    # Cancel text input without drawing anything
                    typing = False
                    text_pos = None
                    typed_text = ""

                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last character
                    typed_text = typed_text[:-1]

                else:
                    # Append the typed character (event.unicode handles special chars)
                    typed_text += event.unicode

            else:
                # Normal mode — keyboard shortcuts
                if event.key == pygame.K_1:
                    brush_size = 2    # small brush

                elif event.key == pygame.K_2:
                    brush_size = 5    # medium brush

                elif event.key == pygame.K_3:
                    brush_size = 10   # large brush

                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_canvas()     # Ctrl+S to save

                elif event.key == pygame.K_DELETE:
                    clear_canvas()    # Delete key to clear canvas

        # ── Mouse button pressed ──
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Check toolbar button clicks
            for tool, rect in tool_buttons.items():
                if rect.collidepoint(mouse_pos):
                    current_tool = tool
                    typing = False   # cancel text mode if switching tools

            for color, rect in color_buttons:
                if rect.collidepoint(mouse_pos):
                    current_color = color

            for size, rect in size_buttons.items():
                if rect.collidepoint(mouse_pos):
                    brush_size = size

            # Handle drawing only if the click is on the canvas (not the toolbar)
            if is_on_canvas(mouse_pos):
                canvas_pos = screen_to_canvas(mouse_pos)  # convert to canvas coords

                if current_tool == "clear":
                    clear_canvas()

                elif current_tool == "fill":
                    # Flood fill from the clicked position
                    flood_fill(canvas, canvas_pos, current_color)

                elif current_tool == "text":
                    # Enter text mode at the clicked position
                    typing = True
                    text_pos = canvas_pos
                    typed_text = ""

                else:
                    # Start a drag for brush, eraser, or any shape tool
                    drawing = True
                    start_pos = canvas_pos
                    last_pos  = canvas_pos

                    # For brush/eraser: draw a dot at the click point immediately
                    # so single clicks (without dragging) still leave a mark
                    if current_tool == "brush":
                        pygame.draw.circle(canvas, current_color, canvas_pos, max(1, brush_size // 2))

                    elif current_tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, canvas_pos, brush_size)

        # ── Mouse moved while button held ──
        elif event.type == pygame.MOUSEMOTION:
            if drawing and is_on_canvas(event.pos):
                canvas_pos = screen_to_canvas(event.pos)

                if current_tool == "brush":
                    # Draw a line from the last position to the current one
                    # This creates smooth strokes even at fast mouse speeds
                    pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size)
                    last_pos = canvas_pos  # update for the next motion event

                elif current_tool == "eraser":
                    pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, brush_size)
                    last_pos = canvas_pos

        # ── Mouse button released ──
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and is_on_canvas(event.pos):
                end_pos = screen_to_canvas(event.pos)

                # For shape tools: the final shape is drawn on mouse release
                # (during drag we only showed a preview on a temp surface)
                if current_tool in [
                    "line", "rectangle", "circle", "square",
                    "right triangle", "equilateral", "rhombus"
                ]:
                    draw_shape(canvas, current_tool, current_color, start_pos, end_pos, brush_size)

            # Reset drag state regardless of where the button was released
            drawing   = False
            start_pos = None
            last_pos  = None

    # 6. Push the frame to the screen and wait for next frame
    pygame.display.update()
    clock.tick(60)  # limit to 60 frames per second to avoid wasting CPU

pygame.quit()  # clean up pygame resources when the loop ends