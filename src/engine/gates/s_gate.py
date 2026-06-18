"""S gate — Phase gate (√Z): 90° rotation over Z-axis."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_S_MAT = ((1, 0), (0, 1j))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _S_MAT)


register(GateDef(
    id="s_gate",
    name="S Gate",
    tip="Phase: 90° rotation over Z-axis",
    color=(240, 160, 200),
    category=Category.SINGLE,
    transform=_transform,
    order=24,
))
