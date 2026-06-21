"""Hadamard gate — creates superposition.

H|0⟩ = |+⟩,  H|1⟩ = |−>,  H|+⟩ = |0⟩,  H|−> = |1⟩
"""

from __future__ import annotations

import math
from ..gate_registry import register, GateDef, Category

_S = 1 / math.sqrt(2)
_H = ((_S, _S), (_S, -_S))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _H)


register(GateDef(
    id="hadamard",
    name="Hadamard",
    tip="Creates superposition",
    color=(190, 135, 255),
    category=Category.SINGLE,
    transform=_transform,

    order=20,
))
