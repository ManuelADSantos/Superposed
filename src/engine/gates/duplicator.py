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


register(GateDef(
    id="duplicator",
    name="Duplicator",
    tip="Copies qubit (straight + CW)",
    color=(100, 200, 140),
    category=Category.ROUTER,
    transform=_transform,

    order=55,
))
