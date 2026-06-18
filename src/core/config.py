"""Game configuration and constants."""

from __future__ import annotations

# Display settings — WIDTH and HEIGHT are fallback defaults.
# main.py overwrites them at startup with the actual display size.
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Game world settings
TILE_SIZE = 64

# Physics
BELT_SPEED = 1.5
GENERATOR_SPEED = 1.5
CNOT_PROCESS_DELAY = 0.15

# UI layout
TOOLBAR_HEIGHT = 72
TOOLBAR_PAD = 8
TOOLTIP_FONT_SIZE = 14
UI_FONT_SIZE = 16

# Colours – dark theme
BG = (14, 14, 18)
GRID_COLOR = (32, 32, 40)

WHITE = (230, 230, 230)
LIGHT_GRAY = (160, 160, 170)
DARK_GRAY = (60, 60, 70)
RED = (220, 80, 80)
GREEN = (100, 220, 120)
BLUE = (100, 160, 255)
PURPLE = (170, 90, 255)
CYAN = (90, 220, 230)
GOLD = (255, 200, 60)

SPEED_MULT = 1
ADMIN_MODE = False
