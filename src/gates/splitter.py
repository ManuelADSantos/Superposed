"""Splitter — routes qubits by measured state.

|0⟩ goes straight (gate direction), |1⟩ goes CW perpendicular.
Superposition collapses first (implicit measurement).
"""

import random
from gate_registry import register, GateDef, Category


def _transform(sx, sy, tile, item, eject_fn):
    """Measure if needed, then route by state."""
    from entities import QubitState, cw_dir, DIR_VECTORS
    from world import get_entangled_partners, break_entanglement

    # Collapse superposition
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

    if item.state == QubitState.ZERO:
        out_dir = tile.direction
    else:
        out_dir = cw_dir(tile.direction)

    dx, dy = DIR_VECTORS[out_dir]
    eject_fn(sx, sy, sx + dx, sy + dy, item)


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _arrow, _a
    from config import WHITE
    from entities import cw_dir
    COLOR = (90, 220, 200)
    TEAL = (70, 200, 190)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (30, 85, 80), COLOR, 10)
    _arrow(s, b.centerx, b.centery, d, _a((220, 80, 80), 200), int(size * 0.16), 2)
    _arrow(s, b.centerx, b.centery, cw_dir(d), _a((100, 160, 255), 200), int(size * 0.16), 2)
    dm = 8
    diamond = [
        (b.centerx, b.centery - dm), (b.centerx + dm, b.centery),
        (b.centerx, b.centery + dm), (b.centerx - dm, b.centery),
    ]
    pygame.draw.polygon(s, _a(TEAL, 200), diamond)
    pygame.draw.polygon(s, _a(WHITE, 150), diamond, 2)
    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="splitter",
    name="Splitter",
    tip="Routes by state",
    color=(90, 220, 200),
    category=Category.ROUTER,
    transform=_transform,
    sprite_fn=_sprite,
    order=50,
))
