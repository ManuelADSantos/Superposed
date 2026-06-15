"""Noise gate — randomly corrupts qubits (50% bit flip)."""

from __future__ import annotations

import random
from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if random.random() < 0.5:
        if item.state == QubitState.ZERO:
            item.state = QubitState.ONE
        elif item.state == QubitState.ONE:
            item.state = QubitState.ZERO
        elif item.state == QubitState.SUPERPOSITION:
            item.phase_flipped = not item.phase_flipped


register(GateDef(
    id="noise",
    name="Noise",
    tip="Random corruption",
    color=(200, 70, 70),
    category=Category.SINGLE,
    transform=_transform,

    order=60,
))
