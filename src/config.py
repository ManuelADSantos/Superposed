"""Game configuration and constants."""

# Display settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Game world settings
TILE_SIZE = 64

# Physics
BELT_SPEED = 1.5
GENERATOR_SPEED = 1.5
CNOT_PROCESS_DELAY = 0.15  # brief pause before CNOT fires

# UI layout
TOOLBAR_HEIGHT = 72
TOOLBAR_PAD = 8
TOOLTIP_FONT_SIZE = 14
UI_FONT_SIZE = 16

# Colors – dark theme
BG = (14, 14, 18)
GRID_COLOR = (32, 32, 40)
GRID_ORIGIN = (48, 48, 60)  # slightly brighter axes

WHITE = (230, 230, 230)
LIGHT_GRAY = (160, 160, 170)
DARK_GRAY = (60, 60, 70)
YELLOW = (255, 220, 90)
RED = (220, 80, 80)
GREEN = (100, 220, 120)
BLUE = (100, 160, 255)
ORANGE = (255, 160, 80)
PURPLE = (170, 90, 255)
CYAN = (90, 220, 230)
TEAL = (70, 200, 190)
PINK = (240, 120, 180)
GOLD = (255, 200, 60)

# Building accent colors (used for toolbar icons & labels)
BELT_COLOR = (84, 136, 210)
GENERATOR_COLOR = (108, 220, 136)
HADAMARD_COLOR = (190, 135, 255)
X_GATE_COLOR = (115, 240, 240)
Z_GATE_COLOR = (240, 120, 180)
CNOT_COLOR = (255, 180, 80)
MEASUREMENT_COLOR = (255, 214, 112)
SPLITTER_COLOR = (90, 220, 200)
SINK_COLOR = (220, 200, 255)
