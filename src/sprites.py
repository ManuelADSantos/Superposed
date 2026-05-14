"""Sprite generation and caching for buildings and qubits.

Custom PNGs: drop a file named <building>.png (e.g. belt.png, hadamard.png)
into the  ../sprites/  directory.  The sprite should face RIGHT; the game
will rotate it automatically for other directions.
"""

from functools import lru_cache
import math
import os

import pygame

from config import (
    RED, BLUE, PURPLE, WHITE, YELLOW, CYAN, PINK, GOLD,
    BELT_COLOR, GENERATOR_COLOR, HADAMARD_COLOR, X_GATE_COLOR,
    Z_GATE_COLOR, CNOT_COLOR, MEASUREMENT_COLOR, SPLITTER_COLOR,
    SINK_COLOR, TEAL,
)
from entities import BuildingType, QubitState, Direction


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def _a(color, alpha):
    return (*color[:3], alpha)


def _surf(size):
    return pygame.Surface((size, size), pygame.SRCALPHA)


def _shadow(surface, rect, radius):
    pygame.draw.rect(surface, (0, 0, 0, 70), rect.move(2, 3), border_radius=radius)


def _panel(surface, rect, base, border, radius=10):
    _shadow(surface, rect, radius)
    pygame.draw.rect(surface, _a(base, 255), rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


def _shine(surface, size):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.line(s, (255, 255, 255, 35), (8, 8), (size - 10, 10), 2)
    surface.blit(s, (0, 0))


def _dir_edge(rect, d):
    m = 10
    if d == Direction.UP:
        return pygame.Rect(rect.left + m, rect.top + 6, rect.width - 2 * m, 8)
    if d == Direction.RIGHT:
        return pygame.Rect(rect.right - 14, rect.top + m, 8, rect.height - 2 * m)
    if d == Direction.DOWN:
        return pygame.Rect(rect.left + m, rect.bottom - 14, rect.width - 2 * m, 8)
    return pygame.Rect(rect.left + 6, rect.top + m, 8, rect.height - 2 * m)


def _dir_mark(surface, d, rect, color):
    edge = _dir_edge(rect, d)
    g = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(g, _a(color, 100), edge, border_radius=4)
    surface.blit(g, (0, 0))


def _arrow(surface, cx, cy, d, color, length=10, width=3):
    """Draw a small direction arrow."""
    from entities import DIR_VECTORS
    dx, dy = DIR_VECTORS[d]
    ex, ey = cx + dx * length, cy + dy * length
    pygame.draw.line(surface, color, (cx, cy), (ex, ey), width)
    # arrowhead
    perp_x, perp_y = -dy, dx
    tip = 5
    pygame.draw.polygon(surface, color, [
        (ex, ey),
        (ex - dx * tip + perp_x * tip * 0.5, ey - dy * tip + perp_y * tip * 0.5),
        (ex - dx * tip - perp_x * tip * 0.5, ey - dy * tip - perp_y * tip * 0.5),
    ])


# ---------------------------------------------------------------------------
# Building sprites
# ---------------------------------------------------------------------------

def _draw_belt(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (36, 60, 95), BELT_COLOR, 10)
    inner = b.inflate(-10, -10)
    pygame.draw.rect(s, (20, 32, 50), inner, border_radius=7)
    pygame.draw.rect(s, _a(BELT_COLOR, 160), inner, 2, border_radius=7)
    _dir_mark(s, d, b, (165, 210, 255))
    _arrow(s, b.centerx, b.centery, d, _a(WHITE, 140), length=int(size * 0.18))
    _shine(s, size)
    return s


def _draw_generator(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (28, 75, 52), GENERATOR_COLOR, 10)
    r = int(size * 0.2)
    pygame.draw.circle(s, (70, 255, 150), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 100), b.center, r, 2)
    pygame.draw.circle(s, _a(GENERATOR_COLOR, 80), b.center, r + 6, 2)
    _dir_mark(s, d, b, (180, 255, 210))
    _shine(s, size)
    return s


def _draw_hadamard(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (65, 34, 115), HADAMARD_COLOR, 10)
    diamond = [
        (b.centerx, b.top + 8), (b.right - 10, b.centery),
        (b.centerx, b.bottom - 8), (b.left + 10, b.centery),
    ]
    pygame.draw.polygon(s, (200, 160, 255), diamond)
    pygame.draw.polygon(s, _a(WHITE, 180), diamond, 2)
    font = pygame.font.SysFont("consolas", max(12, int(size * 0.3)), bold=True)
    txt = font.render("H", True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    _dir_mark(s, d, b, (220, 185, 255))
    return s


def _draw_x_gate(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (24, 80, 85), X_GATE_COLOR, 10)
    ins = b.inflate(-16, -16)
    pygame.draw.line(s, _a(WHITE, 200), ins.topleft, ins.bottomright, 5)
    pygame.draw.line(s, _a(WHITE, 200), ins.topright, ins.bottomleft, 5)
    pygame.draw.line(s, CYAN, ins.topleft, ins.bottomright, 2)
    pygame.draw.line(s, CYAN, ins.topright, ins.bottomleft, 2)
    _dir_mark(s, d, b, (150, 250, 255))
    return s


def _draw_z_gate(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (100, 45, 80), Z_GATE_COLOR, 10)
    font = pygame.font.SysFont("consolas", max(12, int(size * 0.34)), bold=True)
    txt = font.render("Z", True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    # decorative ring
    pygame.draw.circle(s, _a(PINK, 100), b.center, int(size * 0.24), 2)
    _dir_mark(s, d, b, PINK)
    return s


def _draw_cnot(d, size):
    """CNOT: shows control (dot) and target (⊕) with flow arrows."""
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (100, 70, 30), CNOT_COLOR, 10)

    from entities import ccw_dir, cw_dir, opposite_dir
    # Control dot (input side = CCW perp)
    ctrl_in = ccw_dir(d)
    ctrl_out = cw_dir(d)
    # Draw vertical line through center
    pygame.draw.line(s, _a(WHITE, 140), (b.centerx, b.top + 8), (b.centerx, b.bottom - 8), 2)
    pygame.draw.line(s, _a(WHITE, 140), (b.left + 8, b.centery), (b.right - 8, b.centery), 2)
    # Control dot
    r_dot = max(4, int(size * 0.08))
    ctrl_offset = int(size * 0.18)
    from entities import DIR_VECTORS
    cdx, cdy = DIR_VECTORS[ctrl_in]
    dot_x = b.centerx + cdx * ctrl_offset
    dot_y = b.centery + cdy * ctrl_offset
    pygame.draw.circle(s, GOLD, (dot_x, dot_y), r_dot)
    # Target ⊕
    tdx, tdy = DIR_VECTORS[opposite_dir(d)]
    targ_x = b.centerx + tdx * ctrl_offset
    targ_y = b.centery + tdy * ctrl_offset
    r_targ = max(5, int(size * 0.12))
    pygame.draw.circle(s, _a(WHITE, 200), (targ_x, targ_y), r_targ, 2)
    pygame.draw.line(s, _a(WHITE, 200), (targ_x - r_targ, targ_y), (targ_x + r_targ, targ_y), 2)
    pygame.draw.line(s, _a(WHITE, 200), (targ_x, targ_y - r_targ), (targ_x, targ_y + r_targ), 2)
    _dir_mark(s, d, b, CNOT_COLOR)
    return s


def _draw_measurement(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (90, 65, 20), MEASUREMENT_COLOR, 10)
    # Eye / lens
    r = int(size * 0.2)
    pygame.draw.circle(s, (255, 236, 180), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 140), b.center, r, 2)
    pygame.draw.circle(s, (90, 65, 20), b.center, max(3, r // 2))
    # Meter bar
    meter = pygame.Rect(0, 0, int(size * 0.54), int(size * 0.14))
    meter.center = (b.centerx, b.bottom - 14)
    pygame.draw.rect(s, (40, 30, 18), meter, border_radius=6)
    pygame.draw.rect(s, _a(MEASUREMENT_COLOR, 180), meter, 2, border_radius=6)
    pygame.draw.line(s, RED, (meter.left + 6, meter.centery), (meter.centerx - 2, meter.centery), 3)
    pygame.draw.line(s, BLUE, (meter.centerx + 2, meter.centery), (meter.right - 6, meter.centery), 3)
    _dir_mark(s, d, b, (255, 225, 145))
    return s


def _draw_splitter(d, size):
    """Splitter: routes |0⟩ straight, |1⟩ perpendicular."""
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (30, 85, 80), SPLITTER_COLOR, 10)
    from entities import cw_dir
    # Two arrows showing split paths
    _arrow(s, b.centerx, b.centery, d, _a(RED, 200), int(size * 0.16), 2)
    _arrow(s, b.centerx, b.centery, cw_dir(d), _a(BLUE, 200), int(size * 0.16), 2)
    # Diamond
    dm = 8
    diamond = [
        (b.centerx, b.centery - dm), (b.centerx + dm, b.centery),
        (b.centerx, b.centery + dm), (b.centerx - dm, b.centery),
    ]
    pygame.draw.polygon(s, _a(TEAL, 200), diamond)
    pygame.draw.polygon(s, _a(WHITE, 150), diamond, 2)
    _dir_mark(s, d, b, SPLITTER_COLOR)
    return s


def _draw_output_sink(d, size):
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (55, 45, 90), SINK_COLOR, 10)
    # Funnel / collector shape
    r = int(size * 0.22)
    pygame.draw.circle(s, _a(SINK_COLOR, 180), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 120), b.center, r, 2)
    # Down arrow into center
    pygame.draw.polygon(s, _a(WHITE, 160), [
        (b.centerx, b.centery + 4),
        (b.centerx - 6, b.centery - 4),
        (b.centerx + 6, b.centery - 4),
    ])
    _dir_mark(s, d, b, SINK_COLOR)
    return s


# ---------------------------------------------------------------------------
# Qubit sprite
# ---------------------------------------------------------------------------

def _draw_qubit(state, size, disappearing=False, progress=1.0, entangled=False):
    s = _surf(size)
    cx, cy = size / 2, size / 2

    if disappearing:
        sc = max(0.18, progress)
        radius = max(2, int(size * 0.28 * sc))
    else:
        radius = max(3, int(size * 0.28))

    glow_r = int(radius * 1.8)

    if state == QubitState.SUPERPOSITION:
        base = PURPLE
    elif state == QubitState.ZERO:
        base = RED
    else:
        base = BLUE

    # Glow
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow, _a(base, 55), (int(cx), int(cy)), glow_r)
    s.blit(glow, (0, 0))

    # Core
    pygame.draw.circle(s, _a(base, 255), (int(cx), int(cy)), radius)
    # Highlight
    hx, hy = int(cx - radius * 0.3), int(cy - radius * 0.3)
    pygame.draw.circle(s, _a(WHITE, 110), (hx, hy), max(1, radius // 2))

    # Outline
    if entangled:
        # Double ring for entangled qubits
        pygame.draw.circle(s, GOLD, (int(cx), int(cy)), radius + 2, 2)
        pygame.draw.circle(s, _a(GOLD, 100), (int(cx), int(cy)), radius + 5, 1)
    elif state == QubitState.SUPERPOSITION:
        pygame.draw.circle(s, WHITE, (int(cx), int(cy)), radius + 1, 2)
        pygame.draw.circle(s, _a(YELLOW, 140), (int(cx), int(cy)), max(2, radius // 2), 1)
    else:
        pygame.draw.circle(s, _a(WHITE, 130), (int(cx), int(cy)), radius + 1, 1)

    return s


# ---------------------------------------------------------------------------
# Custom PNG sprite loading
# ---------------------------------------------------------------------------

_SPRITE_DIR = os.path.join(os.path.dirname(__file__), '..', 'sprites')
_ROTATION_ANGLE = {
    Direction.RIGHT: 0,
    Direction.UP: 90,
    Direction.LEFT: 180,
    Direction.DOWN: -90,
}


def _load_custom_sprite(building, direction, size):
    """Try to load a custom PNG from ../sprites/<name>.png (faces RIGHT)."""
    name = building.name.lower()
    path = os.path.join(_SPRITE_DIR, f'{name}.png')
    if not os.path.isfile(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (size, size))
        angle = _ROTATION_ANGLE.get(direction, 0)
        if angle:
            img = pygame.transform.rotate(img, angle)
        return img
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Cache wrappers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def get_building_sprite(building, direction, size):
    # Try custom PNG first
    custom = _load_custom_sprite(building, direction, size)
    if custom is not None:
        return custom

    dispatch = {
        BuildingType.BELT: _draw_belt,
        BuildingType.GENERATOR: _draw_generator,
        BuildingType.HADAMARD: _draw_hadamard,
        BuildingType.X_GATE: _draw_x_gate,
        BuildingType.Z_GATE: _draw_z_gate,
        BuildingType.CNOT: _draw_cnot,
        BuildingType.MEASUREMENT: _draw_measurement,
        BuildingType.SPLITTER: _draw_splitter,
        BuildingType.OUTPUT_SINK: _draw_output_sink,
    }
    fn = dispatch.get(building)
    return fn(direction, size) if fn else None


@lru_cache(maxsize=512)
def get_qubit_sprite(state, size, disappearing=False, progress=1.0, entangled=False):
    return _draw_qubit(state, size, disappearing, progress, entangled)
