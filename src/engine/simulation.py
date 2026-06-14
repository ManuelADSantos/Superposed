"""Simulation: qubit movement, gate processing, and factory logic."""

from __future__ import annotations

from ..core.config import BELT_SPEED, GENERATOR_SPEED, CNOT_PROCESS_DELAY
from ..core.entities import (
    QubitState, QubitItem, Direction,
    DIR_VECTORS, opposite_dir, cw_dir, ccw_dir,
)
from ..core import world as _world_mod
from ..core.world import get_tile
from .gate_registry import (
    get_gate, Category,
    EMPTY, BELT, GENERATOR, OUTPUT_SINK,
)


def _start_disappear(item):
    item.is_disappearing = True
    item.disappear_time = 0.3


def _collect_sink(tile, item):
    tile.sink_total += 1
    if tile.sink_target is not None and item.state == tile.sink_target:
        tile.sink_match += 1


def _safe_transform(gate, *args):
    try:
        gate.transform(*args)
    except Exception as exc:
        import sys
        print(f"[Superposed] gate '{gate.id}' transform error: {exc}",
              file=sys.stderr)


def _eject_qubit(src_x, src_y, nx, ny, qubit):
    qubit.progress = 0.0
    next_tile = get_tile(nx, ny)
    gate = get_gate(next_tile.building)
    if gate and gate.category == Category.CONSUMER:
        _safe_transform(gate, qubit, next_tile)
        return
    if next_tile.building == OUTPUT_SINK:
        _collect_sink(next_tile, qubit)
        return
    if next_tile.building != EMPTY and next_tile.item is None:
        next_tile.item = qubit
    else:
        _start_disappear(qubit)


def update_items(dt):
    ready_to_move = []

    for (x, y), tile in list(_world_mod.world.items()):
        if tile.measure_flash > 0:
            tile.measure_flash = max(0.0, tile.measure_flash - dt)

        for slot in ("item", "control_item"):
            q = getattr(tile, slot)
            if q and q.is_disappearing:
                q.disappear_time -= dt
                if q.disappear_time <= 0:
                    setattr(tile, slot, None)

        if tile.building == GENERATOR:
            tile.spawn_timer += dt
            if tile.spawn_timer >= GENERATOR_SPEED and tile.item is None:
                tile.spawn_timer = 0.0
                tile.item = QubitItem(QubitState.ZERO)

        gate = get_gate(tile.building)
        if gate and gate.category == Category.TWO_QUBIT:
            if tile.item and tile.control_item:
                tile.process_timer += dt
                if tile.process_timer >= CNOT_PROCESS_DELAY:
                    _process_two_qubit(x, y, tile, gate)
                    tile.process_timer = 0.0
            else:
                tile.process_timer = 0.0

        if tile.item and not tile.item.is_disappearing:
            should_advance = True
            if gate and gate.category == Category.TWO_QUBIT and tile.control_item:
                should_advance = False
            if should_advance:
                tile.item.progress += BELT_SPEED * dt
                if tile.item.progress >= 1.0:
                    ready_to_move.append((x, y, "item"))

        if tile.control_item and not tile.control_item.is_disappearing:
            tile.control_item.progress += BELT_SPEED * dt

    for x, y, slot in ready_to_move:
        tile = get_tile(x, y)
        item = getattr(tile, slot)
        if item is None or item.is_disappearing:
            continue

        dx, dy = DIR_VECTORS[tile.direction]
        nx, ny = x + dx, y + dy
        item.progress = 0.0

        next_tile = get_tile(nx, ny)
        next_gate = get_gate(next_tile.building)

        if next_gate and next_gate.category == Category.CONSUMER:
            _safe_transform(next_gate, item, next_tile)
            tile.item = None
            continue

        if next_tile.building == OUTPUT_SINK:
            _collect_sink(next_tile, item)
            tile.item = None
            continue

        if next_gate and next_gate.category == Category.ROUTER:
            _safe_transform(next_gate, nx, ny, next_tile, item, _eject_qubit)
            tile.item = None
            continue

        if next_gate and next_gate.category == Category.TWO_QUBIT:
            arrival = opposite_dir(tile.direction)
            target_input = opposite_dir(next_tile.direction)
            control_input = ccw_dir(next_tile.direction)
            if arrival == target_input and next_tile.item is None:
                next_tile.item = item
                tile.item = None
            elif arrival == control_input and next_tile.control_item is None:
                next_tile.control_item = item
                tile.item = None
            continue

        if next_gate and next_gate.category == Category.SINGLE:
            if next_tile.item is None:
                _safe_transform(next_gate, item)
                next_tile.item = item
                tile.item = None
            continue

        if next_tile.building != EMPTY and next_tile.item is None:
            next_tile.item = item
            tile.item = None
        elif next_tile.building == EMPTY:
            _start_disappear(item)


def _process_two_qubit(x, y, tile, gate):
    control = tile.control_item
    target = tile.item
    _safe_transform(gate, control, target)

    dx, dy = DIR_VECTORS[tile.direction]
    _eject_qubit(x, y, x + dx, y + dy, target)
    tile.item = None

    ctrl_dir = cw_dir(tile.direction)
    cdx, cdy = DIR_VECTORS[ctrl_dir]
    _eject_qubit(x, y, x + cdx, y + cdy, control)
    tile.control_item = None
