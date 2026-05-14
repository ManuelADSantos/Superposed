"""Simulation: qubit movement, gate processing, and factory logic."""

import random

from config import BELT_SPEED, GENERATOR_SPEED, CNOT_PROCESS_DELAY
from entities import (
    BuildingType, QubitState, QubitItem, Direction,
    DIR_VECTORS, opposite_dir, cw_dir, ccw_dir, dir_from_delta,
)
from world import get_tile, in_bounds, world
from gates import transform_qubit, record_measurement, apply_cnot, measure_qubit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SINGLE_QUBIT_GATES = {
    BuildingType.HADAMARD,
    BuildingType.X_GATE,
    BuildingType.Z_GATE,
}


def _arrival_dir(src_dir: Direction) -> Direction:
    """Direction a qubit *arrives from* at the next tile, given the source
    tile's direction (= the movement direction)."""
    return opposite_dir(src_dir)


def _can_accept_item(tile) -> bool:
    """Can this tile's main slot accept a new qubit?"""
    if tile.building == BuildingType.EMPTY:
        return False
    if tile.building == BuildingType.CNOT:
        return tile.item is None  # target slot
    return tile.item is None


# ---------------------------------------------------------------------------
# Main update
# ---------------------------------------------------------------------------

def update_items(dt):
    """Advance the simulation by *dt* seconds."""

    ready_to_move = []

    # --- Pass 1: tick timers, spawn, advance progress ----------------------
    for (x, y), tile in list(world.items()):
        # Measurement flash decay
        if tile.measure_flash > 0:
            tile.measure_flash = max(0.0, tile.measure_flash - dt)

        # Disappearing qubits
        for slot_name in ("item", "control_item"):
            q = getattr(tile, slot_name)
            if q and q.is_disappearing:
                q.disappear_time -= dt
                if q.disappear_time <= 0:
                    setattr(tile, slot_name, None)

        # Generator spawning
        if tile.building == BuildingType.GENERATOR:
            tile.spawn_timer += dt
            if tile.spawn_timer >= GENERATOR_SPEED and tile.item is None:
                tile.spawn_timer = 0.0
                tile.item = QubitItem(QubitState.ZERO)

        # CNOT processing: when both slots filled, wait a beat then fire
        if tile.building == BuildingType.CNOT:
            if tile.item and tile.control_item:
                tile.process_timer += dt
                if tile.process_timer >= CNOT_PROCESS_DELAY:
                    _process_cnot(x, y, tile)
                    tile.process_timer = 0.0
            else:
                tile.process_timer = 0.0

        # Advance main item progress
        if tile.item and not tile.item.is_disappearing:
            if tile.building != BuildingType.CNOT or tile.control_item is None:
                # Only advance if not waiting for CNOT pair
                tile.item.progress += BELT_SPEED * dt
                if tile.item.progress >= 1.0:
                    ready_to_move.append((x, y, "item"))

        # Advance control item progress (CNOT control slot also moves)
        if tile.control_item and not tile.control_item.is_disappearing:
            tile.control_item.progress += BELT_SPEED * dt
            # control items don't move out on their own; CNOT handles it

    # --- Pass 2: move items to the next tile --------------------------------
    for x, y, slot in ready_to_move:
        tile = get_tile(x, y)
        item = getattr(tile, slot)
        if item is None or item.is_disappearing:
            continue

        dx, dy = DIR_VECTORS[tile.direction]
        nx, ny = x + dx, y + dy
        item.progress = 0.0

        # Edge of explored world: vanish
        if not in_bounds(nx, ny):
            _start_disappear(item)
            continue

        next_tile = get_tile(nx, ny)

        # --- Measurement gate: consume qubit ---
        if next_tile.building == BuildingType.MEASUREMENT:
            outcome = measure_qubit(item)
            record_measurement(next_tile, outcome)
            tile.item = None
            continue

        # --- Output sink: collect qubit ---
        if next_tile.building == BuildingType.OUTPUT_SINK:
            _collect_sink(next_tile, item)
            tile.item = None
            continue

        # --- Splitter: route by state ---
        if next_tile.building == BuildingType.SPLITTER:
            _process_splitter(nx, ny, next_tile, item)
            tile.item = None
            continue

        # --- CNOT: figure out which slot ---
        if next_tile.building == BuildingType.CNOT:
            arrival = _arrival_dir(tile.direction)
            target_input = opposite_dir(next_tile.direction)
            control_input = ccw_dir(next_tile.direction)

            if arrival == target_input and next_tile.item is None:
                next_tile.item = item
                tile.item = None
            elif arrival == control_input and next_tile.control_item is None:
                next_tile.control_item = item
                tile.item = None
            # else: blocked – item stays
            continue

        # --- Single-qubit gates ---
        if next_tile.building in SINGLE_QUBIT_GATES:
            if next_tile.item is None:
                transform_qubit(next_tile.building, item)
                next_tile.item = item
                tile.item = None
            continue

        # --- Belt / Generator / empty next tile ---
        if next_tile.building != BuildingType.EMPTY and next_tile.item is None:
            next_tile.item = item
            tile.item = None
        elif next_tile.building == BuildingType.EMPTY:
            # qubit falls off the factory – vanish
            _start_disappear(item)


# ---------------------------------------------------------------------------
# CNOT processing
# ---------------------------------------------------------------------------

def _process_cnot(x, y, tile):
    """Both control and target are present – apply CNOT and eject."""
    control = tile.control_item
    target = tile.item

    apply_cnot(control, target)

    # Eject target in gate direction
    dx, dy = DIR_VECTORS[tile.direction]
    _eject_qubit(x, y, x + dx, y + dy, target)
    tile.item = None

    # Eject control in CW perpendicular direction
    ctrl_dir = cw_dir(tile.direction)
    cdx, cdy = DIR_VECTORS[ctrl_dir]
    _eject_qubit(x, y, x + cdx, y + cdy, control)
    tile.control_item = None


def _eject_qubit(src_x, src_y, nx, ny, qubit):
    """Try to place a qubit on the next tile; vanish if impossible."""
    qubit.progress = 0.0
    if not in_bounds(nx, ny):
        _start_disappear(qubit)
        return
    next_tile = get_tile(nx, ny)
    if next_tile.building == BuildingType.MEASUREMENT:
        outcome = measure_qubit(qubit)
        record_measurement(next_tile, outcome)
        return
    if next_tile.building == BuildingType.OUTPUT_SINK:
        _collect_sink(next_tile, qubit)
        return
    if next_tile.building != BuildingType.EMPTY and next_tile.item is None:
        next_tile.item = qubit
    else:
        _start_disappear(qubit)


# ---------------------------------------------------------------------------
# Splitter
# ---------------------------------------------------------------------------

def _process_splitter(sx, sy, splitter_tile, item):
    """Route qubit based on state.  |0⟩ → gate direction, |1⟩ → CW perp.
    Superposition → measure first (implicit measurement), then route."""
    if item.state == QubitState.SUPERPOSITION:
        measure_qubit(item)  # collapse

    if item.state == QubitState.ZERO:
        out_dir = splitter_tile.direction
    else:
        out_dir = cw_dir(splitter_tile.direction)

    dx, dy = DIR_VECTORS[out_dir]
    _eject_qubit(sx, sy, sx + dx, sy + dy, item)


# ---------------------------------------------------------------------------
# Output Sink
# ---------------------------------------------------------------------------

def _collect_sink(tile, item):
    """Collect a qubit into an output sink and update stats."""
    tile.sink_total += 1
    if tile.sink_target is not None and item.state == tile.sink_target:
        tile.sink_match += 1
    # qubit is consumed


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _start_disappear(item):
    """Begin the vanish animation."""
    item.is_disappearing = True
    item.disappear_time = 0.3
