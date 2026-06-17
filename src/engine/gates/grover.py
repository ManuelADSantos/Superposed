"""Two-qubit Grover search block, marked state |11>."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_H = 0.5
_GROVER_11 = (
    (-_H, _H, _H, -_H),
    (_H, -_H, _H, -_H),
    (_H, _H, -_H, -_H),
    (_H, _H, _H, _H),
)


def _transform(control, target):
    from ...core.world import apply_two
    apply_two(control, target, _GROVER_11)


register(GateDef(
    id="grover",
    name="Grover",
    tip="Amplifies |11> from two |+> inputs",
    color=(100, 240, 170),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=35,
))
