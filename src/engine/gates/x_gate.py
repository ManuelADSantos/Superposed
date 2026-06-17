"""X (NOT) gate — flips |0> ↔ |1>."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_X = ((0, 1), (1, 0))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _X)


register(GateDef(
    id="x_gate",
    name="X Gate",
    tip="Flips |0>↔|1>",
    color=(115, 240, 240),
    category=Category.SINGLE,
    transform=_transform,

    order=21,
))
