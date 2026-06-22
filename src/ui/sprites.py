"""Sprite generation and caching.

Resolution order: custom PNG → generic fallback.
"""

from __future__ import annotations

from functools import lru_cache
import math
import os

import pygame

from ..core import config
from ..core.config import RED, BLUE, PURPLE, WHITE, GOLD
from ..core.entities import QubitState, Direction


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



_GATES_SPRITE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'gates_sprites')
_HUD_SPRITE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'hud_sprites')
_ROTATION_ANGLE = {
    Direction.RIGHT: 0, Direction.UP: 90,
    Direction.LEFT: 180, Direction.DOWN: -90,
}


def _load_custom_png(gate_id, direction, size, role=1):
    names = [f"{gate_id}_{role}.png"]
    if role == 1:
        names.append(f"{gate_id}.png")
    path = next((os.path.join(_GATES_SPRITE_DIR, name)
                 for name in names
                 if os.path.isfile(os.path.join(_GATES_SPRITE_DIR, name))), None)
    if path is None:
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


def _generic_sprite(gate_id, direction, size):
    from ..engine.gate_registry import get_gate
    gate = get_gate(gate_id)
    color = gate.color if gate else (120, 120, 130)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, tuple(c // 3 for c in color), color, 10)
    label = (gate.name[:3].upper()) if gate else "?"
    font = config.game_font(max(10, int(size * 0.28)), bold=True)
    txt = font.render(label, True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    _dir_mark(s, direction, b, color)
    return s


def _draw_qubit(state, size, disappearing=False, progress=1.0, entangled=False,
                phase_flipped=False, phase_angle=None, bloch=None):
    s = _surf(size)
    cx, cy = size / 2, size / 2
    if disappearing:
        sc = max(0.18, progress)
        radius = max(2, int(size * 0.36 * sc))
    else:
        radius = max(4, int(size * 0.36))
    glow_r = int(radius * 1.8)
    if state == QubitState.ZERO:
        base = RED
    elif state == QubitState.ONE:
        base = BLUE
    else:
        base = PURPLE
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow, _a(base, 55), (int(cx), int(cy)), glow_r)
    s.blit(glow, (0, 0))
    pygame.draw.circle(s, _a(base, 255), (int(cx), int(cy)), radius)
    _draw_bloch(s, cx, cy, radius, bloch)
    if entangled:
        pygame.draw.circle(s, _a(GOLD, 80), (int(cx), int(cy)), radius + 6, 3)
        pygame.draw.circle(s, GOLD, (int(cx), int(cy)), radius + 3, 3)
    pygame.draw.circle(s, _a(WHITE, 130 if state in (QubitState.ZERO, QubitState.ONE) else 220),
                       (int(cx), int(cy)), radius + 1, 2)
    if state not in (QubitState.ZERO, QubitState.ONE):
        angle = phase_angle if phase_angle is not None else (math.pi if phase_flipped else 0.0)
        _draw_phase_tick(s, cx, cy, radius, angle)
    return s


# Screen-space axis vectors (right=+sx, down=+sy)
# Z: up, Y: right, X: bottom-left at 45° from vertical, foreshortened for depth
_BPX = (-math.sin(math.radians(45)) * 0.5, math.cos(math.radians(45)) * 0.5)
_BPY = (1.0, 0.0)
_BPZ = (0.0, -1.0)


def _bloch_proj(cx, cy, r, x, y, z):
    return (int(cx + (x * _BPX[0] + y * _BPY[0] + z * _BPZ[0]) * r),
            int(cy + (x * _BPX[1] + y * _BPY[1] + z * _BPZ[1]) * r))


def _draw_bloch(surface, cx, cy, radius, bloch):
    if bloch is None:
        return
    r = max(2, int(radius * 0.58))
    center = (int(cx), int(cy))
    pygame.draw.circle(surface, WHITE, center, r, 1)
    eq = [_bloch_proj(cx, cy, r, math.cos(a), math.sin(a), 0)
          for a in (i * math.pi / 16 for i in range(32))]
    pygame.draw.polygon(surface, WHITE, eq, 1)
    for ax in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        pygame.draw.line(surface, WHITE,
                         _bloch_proj(cx, cy, r, -ax[0], -ax[1], -ax[2]),
                         _bloch_proj(cx, cy, r, *ax), 1)
    ex, ey = _bloch_proj(cx, cy, r, *bloch)
    lw = max(1, int(radius * 0.12))
    pygame.draw.circle(surface, WHITE, (ex, ey), lw)


def _draw_phase_tick(surface, cx, cy, radius, angle):
    ux, uy = math.sin(angle), math.cos(angle)
    r_inner = radius - 1
    r_outer = radius + max(3, int(radius * 0.45))
    tip = (int(cx + ux * r_outer), int(cy + uy * r_outer))
    px, py = -uy, ux
    hw = max(2, int(radius * 0.25))
    base_l = (int(cx + ux * r_inner + px * hw), int(cy + uy * r_inner + py * hw))
    base_r = (int(cx + ux * r_inner - px * hw), int(cy + uy * r_inner - py * hw))
    pygame.draw.polygon(surface, WHITE, [tip, base_l, base_r])


@lru_cache(maxsize=512)
def get_qubit_sprite(state, size, disappearing=False, progress=1.0, entangled=False,
                     phase_flipped=False, phase_angle=None, bloch=None):
    return _draw_qubit(state, size, disappearing, progress, entangled,
                       phase_flipped, phase_angle, bloch)


# ponytail: gates that always face RIGHT regardless of tile rotation
_ORIENTATION_LOCKED = frozenset({"measurement", "output_sink", "noise"})


def _ctrl_sprite(building_id, direction, size):
    """Fallback control-dot sprite for multi-qubit companion cells."""
    from ..engine.gate_registry import get_gate
    gate = get_gate(building_id)
    color = gate.color if gate else (120, 120, 130)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, tuple(c // 3 for c in color), color, 10)
    r = max(4, int(size * 0.16))
    pygame.draw.circle(s, _a(color, 255), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 180), b.center, r, 2)
    _dir_mark(s, direction, b, color)
    return s


@lru_cache(maxsize=512)
def get_building_sprite(building_id, direction, size, ctrl=False, role=1):
    if building_id == "empty":
        return None
    if ctrl and role == 1:
        role = 2
    if role != 1:
        custom = _load_custom_png(building_id, direction, size, role)
        if custom is not None:
            return custom
        return _ctrl_sprite(building_id, direction, size)
    if building_id in _ORIENTATION_LOCKED:
        direction = Direction.RIGHT
    custom = _load_custom_png(building_id, direction, size, role)
    if custom is not None:
        return custom
    return _generic_sprite(building_id, direction, size)


@lru_cache(maxsize=128)
def get_hud_sprite(building_id, size):
    path = os.path.join(_HUD_SPRITE_DIR, f"{building_id}.png")
    if os.path.isfile(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (size, size))
        except Exception:
            pass
    return get_building_sprite(building_id, Direction.RIGHT, size)


def clear_sprite_caches():
    get_building_sprite.cache_clear()
    get_qubit_sprite.cache_clear()
    get_hud_sprite.cache_clear()
