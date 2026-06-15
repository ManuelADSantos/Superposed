"""Duplicator — copies a qubit and sends both directions.

Original exits straight (gate direction), copy exits CW.
Superposition collapses before copying (no-cloning theorem).
"""

from __future__ import annotations

import random
from ..gate_registry import register, GateDef, Category


def _transform(sx, sy, tile, item, eject_fn):
    from ...core.entities import QubitItem, QubitState, DIR_VECTORS, cw_dir
    from ...core.world import get_entangled_partners, break_entanglement

    # ponytail: no-cloning — collapse superposition before copying
    if item.state == QubitState.SUPERPOSITION:
        result = random.choice([QubitState.ZERO, QubitState.ONE])
        item.state = result
        item.phase_flipped = False
        for partner in get_entangled_partners(item):
            if partner.state == QubitState.SUPERPOSITION:
                partner.state = result
                partner.phase_flipped = False
            break_entanglement(partner)
        break_entanglement(item)

    copy = QubitItem(item.state)
    copy.phase_flipped = item.phase_flipped

    dx, dy = DIR_VECTORS[tile.direction]
    eject_fn(sx, sy, sx + dx, sy + dy, item)

    cw = cw_dir(tile.direction)
    cdx, cdy = DIR_VECTORS[cw]
    eject_fn(sx, sy, sx + cdx, sy + cdy, copy)


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _arrow, _a
    from ...core.config import WHITE
    from ...core.entities import cw_dir
    COLOR = (100, 200, 140)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (35, 80, 55), COLOR, 10)
    _arrow(s, b.centerx, b.centery, d, _a(WHITE, 180), int(size * 0.16), 2)
    _arrow(s, b.centerx, b.centery, cw_dir(d), _a(WHITE, 180), int(size * 0.16), 2)
    font = pygame.font.SysFont("consolas", max(10, int(size * 0.22)), bold=True)
    txt = font.render("DUP", True, WHITE)
    s.blit(txt, txt.get_rect(center=(b.centerx, b.centery - 2)))
    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="duplicator",
    name="Duplicator",
    tip="Copies qubit (straight + CW)",
    color=(100, 200, 140),
    category=Category.ROUTER,
    transform=_transform,
    sprite_fn=_sprite,
    order=55,
))
