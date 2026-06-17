"""Toy Shor period-finding block."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category
from .qft import _QFT2


def _transform(control, target):
    from ...core.world import apply_two
    # ponytail: full factoring is content-sized; this is the QFT readout step.
    apply_two(control, target, _QFT2)


register(GateDef(
    id="shor",
    name="Shor",
    tip="Toy period finder (QFT readout)",
    color=(230, 230, 120),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=37,
))
