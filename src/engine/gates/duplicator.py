"""Duplicator — copies a qubit and sends both directions.

Original exits straight (gate direction), copy exits CW.
Superposition collapses before copying (no-cloning theorem).
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(sx, sy, tile, item, eject_fn):
    from ...core.entities import QubitItem, DIR_VECTORS, cw_dir
    from ...core.world import measure_qubit

    # ponytail: no-cloning — collapse superposition before copying
    measure_qubit(item)

    copy = QubitItem()
    copy.alpha, copy.beta = item.alpha, item.beta

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
