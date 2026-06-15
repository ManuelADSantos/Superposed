"""Oracle gates — black-box functions for Deutsch's algorithm.

Constant oracle: identity (does nothing).
Balanced oracle: applies Z (phase flip on superposition).
Both look identical — the circuit reveals which is which.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform_constant(item):
    pass


def _transform_balanced(item):
    from ...core.entities import QubitState
    if item.state == QubitState.SUPERPOSITION:
        item.phase_flipped = not item.phase_flipped


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a
    from ...core.config import WHITE
    COLOR = (160, 100, 220)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (60, 35, 90), COLOR, 10)
    font = pygame.font.SysFont("consolas", max(14, int(size * 0.4)), bold=True)
    txt = font.render("?", True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    pygame.draw.rect(s, _a(COLOR, 120), b.inflate(-12, -12), 2, border_radius=6)
    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="oracle_constant",
    name="Oracle",
    tip="Black-box function",
    color=(160, 100, 220),
    category=Category.SINGLE,
    transform=_transform_constant,
    sprite_fn=_sprite,
    order=70,
))

register(GateDef(
    id="oracle_balanced",
    name="Oracle",
    tip="Black-box function",
    color=(160, 100, 220),
    category=Category.SINGLE,
    transform=_transform_balanced,
    sprite_fn=_sprite,
    order=71,
))
