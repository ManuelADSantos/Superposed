"""X (NOT) gate — flips |0> ↔ |1>."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if item.state == QubitState.ZERO:
        item.state = QubitState.ONE
    elif item.state == QubitState.ONE:
        item.state = QubitState.ZERO


register(GateDef(
    id="x_gate",
    name="X Gate",
    tip="Flips |0>↔|1>",
    color=(115, 240, 240),
    category=Category.SINGLE,
    transform=_transform,

    order=21,
))
