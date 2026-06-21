"""Noise gate — randomises qubit state and exit direction.

Accepts from any side, exits from a random side (excluding input).
"""

from __future__ import annotations

import math
import random
from ..gate_registry import register, GateDef, Category

_S = 1 / math.sqrt(2)
_STATES = [
    (1+0j, 0+0j),           # |0⟩
    (0+0j, 1+0j),           # |1⟩
    (_S+0j, _S+0j),         # |+⟩
    (_S+0j, -_S+0j),        # |−⟩
    (complex(_S), complex(0, _S)),   # |i⟩
    (complex(_S), complex(0, -_S)),  # |−i⟩
]


def _transform(sx, sy, tile, item, eject_fn):
    item.alpha, item.beta = random.choice(_STATES)
    from ...core.entities import Direction, DIR_VECTORS, opposite_dir
    arrival = getattr(item, '_arrival_dir', tile.direction)
    excluded = opposite_dir(arrival)
    choices = [d for d in Direction if d != excluded]
    out_dir = random.choice(choices)
    dx, dy = DIR_VECTORS[out_dir]
    eject_fn(sx, sy, sx + dx, sy + dy, item)


register(GateDef(
    id="noise",
    name="Noise",
    tip="Random corruption",
    color=(200, 70, 70),
    category=Category.ROUTER,
    transform=_transform,

    order=60,
))
