"""Z gate — phase flip, shown by the qubit phase arrow."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_Z = ((1, 0), (0, -1))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _Z)


register(GateDef(
    id="z_gate",
    name="Z Gate",
    tip="Phase flip",
    color=(240, 120, 180),
    category=Category.SINGLE,
    transform=_transform,

    order=22,
))
