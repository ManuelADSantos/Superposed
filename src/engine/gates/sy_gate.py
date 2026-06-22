"""SY gate — √Y: 90° rotation over Y-axis."""

from __future__ import annotations

import math
from ..gate_registry import register, GateDef, Category

_S = 1 / math.sqrt(2)
_SY = ((_S, -_S), (_S, _S))


def _transform(item):
    from ...core.world import apply_single
    apply_single(item, _SY)


register(GateDef(
    id="sy_gate",
    name="√Y",
    tip="90° rotation over Y-axis",
    color=(140, 230, 140),
    category=Category.SINGLE,
    transform=_transform,
    order=26,
))
