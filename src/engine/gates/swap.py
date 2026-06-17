"""SWAP gate — exchanges the quantum states of two qubits.

SWAP(|a>, |b>) = (|b>, |a>)
Uses the same two-input geometry as CNOT.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

# |00>→|00>, |01>→|10>, |10>→|01>, |11>→|11>
_SWAP = ((1,0,0,0), (0,0,1,0), (0,1,0,0), (0,0,0,1))


def _transform(control, target):
    from ...core.world import apply_two
    apply_two(control, target, _SWAP)


register(GateDef(
    id="swap",
    name="SWAP",
    tip="Exchanges two qubit states",
    color=(255, 140, 60),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=32,
))
