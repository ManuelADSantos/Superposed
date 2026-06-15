"""Z gate — phase flip.  |+> ↔ |−> (invisible on basis states)."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if item.state == QubitState.SUPERPOSITION:
        item.phase_flipped = not item.phase_flipped


register(GateDef(
    id="z_gate",
    name="Z Gate",
    tip="Phase flip",
    color=(240, 120, 180),
    category=Category.SINGLE,
    transform=_transform,

    order=22,
))
