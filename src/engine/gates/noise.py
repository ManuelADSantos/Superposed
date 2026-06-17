"""Noise gate — randomly corrupts qubits (50% bit flip)."""

from __future__ import annotations

import random
from ..gate_registry import register, GateDef, Category

_X = ((0, 1), (1, 0))


def _transform(item):
    if random.random() < 0.5:
        from ...core.world import apply_single
        apply_single(item, _X)


register(GateDef(
    id="noise",
    name="Noise",
    tip="Random corruption",
    color=(200, 70, 70),
    category=Category.SINGLE,
    transform=_transform,

    order=60,
))
