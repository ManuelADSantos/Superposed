"""Game configuration and constants."""

from __future__ import annotations

import os
import sys

# ponytail: PyInstaller sets sys._MEIPASS; normal runs use __file__-relative
_BASE = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS_DIR = os.path.join(_BASE, 'assets')

_FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
FONT_PATH = next((os.path.join(_FONTS_DIR, f) for f in os.listdir(_FONTS_DIR)
                   if f.endswith(('.ttf', '.otf'))), None)

_font_cache = {}


def game_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        import pygame
        if FONT_PATH:
            f = pygame.font.Font(FONT_PATH, size)
        else:
            f = pygame.font.SysFont("consolas", size)
        if bold:
            f.set_bold(True)
        _font_cache[key] = f
    return _font_cache[key]

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
DARK_GRAY = (120, 120, 120)
RED = (220, 80, 80)
GREEN = (100, 220, 120)
BLUE = (100, 160, 255)
PURPLE = (170, 90, 255)
CYAN = (90, 220, 230)
GOLD = (255, 200, 60)

SPEED_MULT = 1
ADMIN_MODE = False
