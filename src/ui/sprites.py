"""Sprite generation and caching.

Resolution order: custom PNG -> gate.sprite_fn -> generic fallback.
"""

from __future__ import annotations

from functools import lru_cache
import os

import pygame

from ..core.config import RED, BLUE, PURPLE, WHITE, YELLOW, GOLD, PINK
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
_ROTATION_ANGLE = {
    Direction.RIGHT: 0, Direction.UP: 90,
    Direction.LEFT: 180, Direction.DOWN: -90,
}


def _load_custom_png(gate_id, direction, size):
    path = os.path.join(_GATES_SPRITE_DIR, f'{gate_id}.png')
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


def _generic_sprite(gate_id, direction, size):
    from ..engine.gate_registry import get_gate
    gate = get_gate(gate_id)
    color = gate.color if gate else (120, 120, 130)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, tuple(c // 3 for c in color), color, 10)
    label = (gate.name[:3].upper()) if gate else "?"
    font = pygame.font.SysFont("consolas", max(10, int(size * 0.28)), bold=True)
    txt = font.render(label, True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    _dir_mark(s, direction, b, color)
    return s


def _draw_qubit(state, size, disappearing=False, progress=1.0, entangled=False, phase_flipped=False):
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
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow, _a(base, 55), (int(cx), int(cy)), glow_r)
    s.blit(glow, (0, 0))
    pygame.draw.circle(s, _a(base, 255), (int(cx), int(cy)), radius)
    hx, hy = int(cx - radius * 0.3), int(cy - radius * 0.3)
    pygame.draw.circle(s, _a(WHITE, 110), (hx, hy), max(1, radius // 2))
    if entangled:
        pygame.draw.circle(s, GOLD, (int(cx), int(cy)), radius + 2, 2)
        pygame.draw.circle(s, _a(GOLD, 100), (int(cx), int(cy)), radius + 5, 1)
    elif state == QubitState.SUPERPOSITION:
        if phase_flipped:
            pygame.draw.circle(s, PINK, (int(cx), int(cy)), radius + 1, 2)
            d = max(2, radius // 2)
            pygame.draw.line(s, _a(WHITE, 200),
                             (int(cx) - d, int(cy)), (int(cx) + d, int(cy)), 2)
        else:
            pygame.draw.circle(s, WHITE, (int(cx), int(cy)), radius + 1, 2)
            pygame.draw.circle(s, _a(YELLOW, 140), (int(cx), int(cy)), max(2, radius // 2), 1)
    else:
        pygame.draw.circle(s, _a(WHITE, 130), (int(cx), int(cy)), radius + 1, 1)
    return s


@lru_cache(maxsize=512)
def get_qubit_sprite(state, size, disappearing=False, progress=1.0, entangled=False, phase_flipped=False):
    return _draw_qubit(state, size, disappearing, progress, entangled, phase_flipped)


# ponytail: gates that always face RIGHT regardless of tile rotation
_ORIENTATION_LOCKED = frozenset({"measurement", "output_sink"})


@lru_cache(maxsize=512)
def get_building_sprite(building_id, direction, size):
    if building_id == "empty":
        return None
    if building_id in _ORIENTATION_LOCKED:
        direction = Direction.RIGHT
    custom = _load_custom_png(building_id, direction, size)
    if custom is not None:
        return custom
    from ..engine.gate_registry import get_gate
    gate = get_gate(building_id)
    if gate and gate.sprite_fn:
        return gate.sprite_fn(direction, size)
    return _generic_sprite(building_id, direction, size)


def clear_sprite_caches():
    get_building_sprite.cache_clear()
    get_qubit_sprite.cache_clear()
