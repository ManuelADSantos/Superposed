"""CNOT gate — two-qubit entangling gate.

Control enters from CCW perpendicular, target enters from behind.
If control is |1⟩, target is flipped.
If control is superposition, both become entangled.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

# |00>→|00>, |01>→|01>, |10>→|11>, |11>→|10>
_CNOT = ((1,0,0,0), (0,1,0,0), (0,0,0,1), (0,0,1,0))


def _transform(control, target):
    from ...core.world import apply_two
    apply_two(control, target, _CNOT)


register(GateDef(
    id="cnot",
    name="CNOT",
    tip="Entangles two qubits (C=control, T=target)",
    color=(255, 180, 80),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=30,
))
