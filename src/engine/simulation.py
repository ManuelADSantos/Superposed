"""Simulation: qubit movement, gate processing, and factory logic."""

from __future__ import annotations

import math

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
    from ..core.world import break_entanglement
    break_entanglement(item)
    item.is_disappearing = True
    item.disappear_time = 0.3


def _collect_sink(tile, item):
    from ..core.world import break_entanglement
    state = item.state
    phase = item.phase_angle
    break_entanglement(item)
    tile.sink_total += 1
    if tile.sink_target is None:
        return
    if state != tile.sink_target:
        return
    if tile.sink_phase is not None:
        diff = abs((phase - tile.sink_phase + math.pi) % (2 * math.pi) - math.pi)
        if diff > 0.15:
            return
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


def _multi_tiles(px, py, primary, gate):
    dx, dy = DIR_VECTORS[ccw_dir(primary.direction)]
    return [
        (px + dx * i, py + dy * i, get_tile(px + dx * i, py + dy * i))
        for i in range(gate.qubits)
    ]


_spawn_clock = 0.0


def reset_spawn_clock():
    global _spawn_clock
    _spawn_clock = 0.0


def _spawn_qubit(tile):
    q = QubitItem(tile.spawn_state or QubitState.ZERO)
    if tile.spawn_phase is not None:
        phase = complex(math.cos(tile.spawn_phase), math.sin(tile.spawn_phase))
        if q.state == QubitState.ZERO:
            q.alpha *= phase
        else:
            q.beta *= phase
    return q


def update_items(dt):
    global _spawn_clock
    ready_to_move = []

    _spawn_clock += dt
    spawn_now = _spawn_clock >= GENERATOR_SPEED
    if spawn_now:
        _spawn_clock -= GENERATOR_SPEED

    for (x, y), tile in list(_world_mod.world.items()):
        if tile.measure_flash > 0:
            tile.measure_flash = max(0.0, tile.measure_flash - dt)

        if tile.item and tile.item.is_disappearing:
            tile.item.disappear_time -= dt
            if tile.item.disappear_time <= 0:
                tile.item = None

        if tile.building == GENERATOR and spawn_now and tile.item is None:
            tile.item = _spawn_qubit(tile)

        gate = get_gate(tile.building)

        # Multi-qubit gate processing: only on primary (target) tile
        if gate and gate.category == Category.TWO_QUBIT and tile.peer and not tile.is_ctrl:
            cells = _multi_tiles(x, y, tile, gate)
            if all(cell.item for _, _, cell in cells):
                tile.process_timer += dt
                if tile.process_timer >= CNOT_PROCESS_DELAY:
                    _process_multi_qubit(x, y, tile, gate)
                    tile.process_timer = 0.0
            else:
                tile.process_timer = 0.0

        if tile.item and not tile.item.is_disappearing:
            if gate and gate.category == Category.TWO_QUBIT and tile.peer:
                # Items on multi-qubit tiles advance to 1.0 then hold
                if tile.item.progress < 1.0:
                    tile.item.progress = min(1.0, tile.item.progress + BELT_SPEED * dt)
            else:
                tile.item.progress += BELT_SPEED * dt
                if tile.item.progress >= 1.0:
                    ready_to_move.append((x, y))

    for x, y in ready_to_move:
        tile = get_tile(x, y)
        item = tile.item
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

        if next_gate and next_gate.category == Category.TWO_QUBIT and next_tile.peer:
            # Multi-cell gate: accept qubit from behind only
            arrival = opposite_dir(tile.direction)
            expected = opposite_dir(next_tile.direction)
            if arrival == expected and next_tile.item is None:
                next_tile.item = item
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


def _process_multi_qubit(px, py, primary, gate):
    cells = _multi_tiles(px, py, primary, gate)
    items = [tile.item for _, _, tile in cells]
    target = items[0]
    controls = items[1:]
    _safe_transform(gate, *controls, target)
    dx, dy = DIR_VECTORS[primary.direction]
    for x, y, tile in cells:
        _eject_qubit(x, y, x + dx, y + dy, tile.item)
        tile.item = None
