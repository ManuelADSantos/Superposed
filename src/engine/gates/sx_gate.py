"""SX gate — √X: 90° rotation over X-axis."""

from __future__ import annotations

import math
from ..gate_registry import register, GateDef, Category

_S = 1 / math.sqrt(2)
_SX = ((_S, -_S * 1j), (-_S * 1j, _S))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _SX)


register(GateDef(
    id="sx_gate",
    name="√X",
    tip="90° rotation over X-axis",
    color=(160, 240, 240),
    category=Category.SINGLE,
    transform=_transform,
    order=25,
))
