"""SWAP gate — exchanges the quantum states of two qubits.

After a SWAP, each qubit carries the other's original state (and phase).
Useful for crossing qubit streams and rerouting without changing states.

  SWAP(|a>, |b>) = (|b>, |a>)

Uses the same two-input geometry as CNOT:
  Target  enters from behind (opposite of facing direction).
  "Control" enters from the CCW-perpendicular side.
Both labels are symmetric — SWAP doesn't distinguish them by role.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(control, target):
    """Swap quantum states between the two qubits."""
    from ...core.world import break_entanglement
    # Exchange states and phases
    control.state, target.state = target.state, control.state
    control.phase_flipped, target.phase_flipped = (
        target.phase_flipped, control.phase_flipped
    )
    # Break entanglement — each qubit is now in a new stream context
    break_entanglement(control)
    break_entanglement(target)


register(GateDef(
    id="swap",
    name="SWAP",
    tip="Exchanges two qubit states",
    color=(255, 140, 60),
    category=Category.TWO_QUBIT,
    transform=_transform,

    order=32,
))
