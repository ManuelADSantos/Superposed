"""Splitter — routes qubits by measured state.

|0> goes straight (gate direction), |1> goes CW perpendicular.
Superposition collapses first (implicit measurement).
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(sx, sy, tile, item, eject_fn):
    """Measure if needed, then route by state."""
    from ...core.entities import QubitState, cw_dir, DIR_VECTORS
    from ...core.world import measure_qubit

    result = measure_qubit(item)
    out_dir = tile.direction if result == QubitState.ZERO else cw_dir(tile.direction)
    dx, dy = DIR_VECTORS[out_dir]
    eject_fn(sx, sy, sx + dx, sy + dy, item)


register(GateDef(
    id="splitter",
    name="Splitter",
    tip="Routes by state",
    color=(90, 220, 200),
    category=Category.ROUTER,
    transform=_transform,

    order=50,
))
