"""CZ gate — Controlled-Z.

Applies Z to the target when control is |1>.
Phase-only: all effects invisible on pure |0>/|1>, show up through interference.
Phase kickback on |+>|1> is now correct with complex amplitudes.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

# |00>→|00>, |01>→|01>, |10>→|10>, |11>→−|11>
_CZ = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,-1))


def _transform(control, target):
    from ...core.world import apply_two
    apply_two(control, target, _CZ)


register(GateDef(
    id="cz",
    name="CZ Gate",
    tip="Controlled phase flip (C=control, T=target)",
    color=(80, 180, 255),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=31,
))
