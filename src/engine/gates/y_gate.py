"""Y gate — Pauli Y.

Y = iXZ: flips |0>↔|1> like X, AND flips the phase like Z.
  Y|0> = |1>
  Y|1> = |0>
  Y|+> = |->   (toggles phase_flipped on superposition)
  Y|-> = |+>
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if item.state == QubitState.ZERO:
        item.state = QubitState.ONE
    elif item.state == QubitState.ONE:
        item.state = QubitState.ZERO
    else:  # SUPERPOSITION
        item.phase_flipped = not item.phase_flipped


register(GateDef(
    id="y_gate",
    name="Y Gate",
    tip="Flips |0>↔|1> + phase flip",
    color=(100, 220, 100),
    category=Category.SINGLE,
    transform=_transform,

    order=23,
))
