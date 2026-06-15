"""Hadamard gate — creates superposition.

H|0> = |+>,  H|1> = |−>,  H|+> = |0>,  H|−> = |1>
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    from ...core.world import break_entanglement
    if item.state in (QubitState.ZERO, QubitState.ONE):
        item.phase_flipped = (item.state == QubitState.ONE)
        item.state = QubitState.SUPERPOSITION
    else:
        if item.phase_flipped:
            item.state = QubitState.ONE
        else:
            item.state = QubitState.ZERO
        item.phase_flipped = False
        break_entanglement(item)


register(GateDef(
    id="hadamard",
    name="Hadamard",
    tip="Creates superposition",
    color=(190, 135, 255),
    category=Category.SINGLE,
    transform=_transform,

    order=20,
))
