"""Toffoli gate — controlled-controlled NOT."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_TOFFOLI = tuple(
    tuple(1 if r == (c ^ 1 if c >= 6 else c) else 0 for c in range(8))
    for r in range(8)
)


def _transform(control_a, control_b, target):
    from ...core.world import apply_many
    apply_many([control_a, control_b, target], _TOFFOLI)


register(GateDef(
    id="toffoli",
    name="Toffoli",
    tip="Flips target only when both controls are |1⟩",
    color=(255, 210, 90),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=3,
    order=33,
))
