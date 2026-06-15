"""CNOT gate — two-qubit entangling gate.

Control enters from CCW perpendicular, target enters from behind.
If control is |1>, target is flipped.
If control is superposition, both become entangled.

Note: entanglement uses same-state correlation only (|00> + |11>).
Anti-correlated pairs are not modeled.  See world.py for details.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(control, target):
    """Apply CNOT: flip target if control is |1>; entangle if superposition."""
    from ...core.entities import QubitState
    from ...core.world import create_entangle_group, register_entangled

    if control.state == QubitState.ONE:
        # Flip target
        if target.state == QubitState.ZERO:
            target.state = QubitState.ONE
        elif target.state == QubitState.ONE:
            target.state = QubitState.ZERO
    elif control.state == QubitState.SUPERPOSITION:
        if target.state in (QubitState.ZERO, QubitState.ONE):
            target.state = QubitState.SUPERPOSITION
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)


register(GateDef(
    id="cnot",
    name="CNOT",
    tip="Entangles two qubits (C=control, T=target)",
    color=(255, 180, 80),
    category=Category.TWO_QUBIT,
    transform=_transform,

    order=30,
))
