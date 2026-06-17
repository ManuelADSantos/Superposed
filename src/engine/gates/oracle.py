"""Oracle gates — black-box functions for Deutsch's algorithm.

Constant oracle: identity (does nothing).
Balanced oracle: applies Z (phase flip on superposition).
Both look identical — the circuit reveals which is which.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_Z = ((1, 0), (0, -1))


def _transform_constant(item):
    pass


def _transform_balanced(item):
    from ...core.world import apply_single
    apply_single(item, _Z)


register(GateDef(
    id="oracle_constant",
    name="Oracle",
    tip="Black-box function",
    color=(160, 100, 220),
    category=Category.SINGLE,
    transform=_transform_constant,
    order=70,
))

register(GateDef(
    id="oracle_balanced",
    name="Oracle",
    tip="Black-box function",
    color=(160, 100, 220),
    category=Category.SINGLE,
    transform=_transform_balanced,
    order=71,
))
