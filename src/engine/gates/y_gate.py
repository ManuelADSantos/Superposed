"""Y gate — Pauli Y: flips |0⟩↔|1⟩ and flips phase on superposition."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_Y = ((0, -1j), (1j, 0))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _Y)


register(GateDef(
    id="y_gate",
    name="Y Gate",
    tip="Flips |0⟩↔|1⟩ + phase flip",
    color=(100, 220, 100),
    category=Category.SINGLE,
    transform=_transform,

    order=23,
))
