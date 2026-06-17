"""Three-cell teleport block: top source state appears on bottom target."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(helper, source, target):
    from ...core.world import break_entanglement

    alpha, beta = source.alpha, source.beta
    # ponytail: high-level teleport; add Bell measurement/feed-forward when puzzles need wires.
    for qubit in (helper, source, target):
        break_entanglement(qubit)
    target.alpha, target.beta = alpha, beta
    helper.alpha, helper.beta = 1 + 0j, 0 + 0j
    source.alpha, source.beta = 1 + 0j, 0 + 0j


register(GateDef(
    id="teleport",
    name="Teleport",
    tip="Moves top source state to bottom target",
    color=(255, 150, 220),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=3,
    order=36,
))
