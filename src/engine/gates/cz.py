"""CZ gate — Controlled-Z.

Applies Z to the target when control is |1>.
Because Z only affects phase, the most visible effect is on superposition.

Key behaviours:
  control=|1>,  target=|+>  ->  target becomes |->  (phase flip)
  control=|+>,  target=|1>  ->  control becomes |->  (phase kickback!)
  control=|+>,  target=|+>  ->  entangled Bell-like state
  control=|0>               ->  nothing happens (Z|anything> when c=0 = identity)

Unlike CNOT (which flips bits), CZ flips phases — all its effects are invisible
on pure |0>/|1> states and only show up through interference.

Control enters from the CCW-perpendicular side (same convention as CNOT).
Target enters from behind.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(control, target):
    from ...core.entities import QubitState
    from ...core.world import create_entangle_group, register_entangled

    if control.state == QubitState.ONE:
        # Apply Z to target: only visible on superposition
        if target.state == QubitState.SUPERPOSITION:
            target.phase_flipped = not target.phase_flipped
        # |0> and |1> are eigenstates of Z — no effect

    elif control.state == QubitState.SUPERPOSITION:
        if target.state == QubitState.ONE:
            # Phase kickback: Z kicks back onto the control qubit's phase
            control.phase_flipped = not control.phase_flipped
        elif target.state == QubitState.SUPERPOSITION:
            # Both in superposition -> entangle
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)
        # target=|0>: Z|0>=|0>, no effect on control either


register(GateDef(
    id="cz",
    name="CZ Gate",
    tip="Controlled phase flip (C=control, T=target)",
    color=(80, 180, 255),
    category=Category.TWO_QUBIT,
    transform=_transform,

    order=31,
))
