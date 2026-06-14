"""Game entities: qubits, tiles, and directions.

Building types are now string IDs managed by gate_registry.
"""

from __future__ import annotations

from enum import Enum

from .config import RED, BLUE, PURPLE, WHITE


# ---------------------------------------------------------------------------
# Directions
# ---------------------------------------------------------------------------

class Direction(Enum):
    """Cardinal directions (ordered CW so arithmetic works)."""
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


DIR_VECTORS = {
    Direction.UP: (0, -1),
    Direction.RIGHT: (1, 0),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
}


def opposite_dir(d: Direction) -> Direction:
    return Direction((d.value + 2) % 4)


def cw_dir(d: Direction) -> Direction:
    return Direction((d.value + 1) % 4)


def ccw_dir(d: Direction) -> Direction:
    return Direction((d.value - 1) % 4)


# ---------------------------------------------------------------------------
# Qubit
# ---------------------------------------------------------------------------

class QubitState(Enum):
    ZERO = 0
    ONE = 1
    SUPERPOSITION = 2


def state_color(state):
    if state == QubitState.ZERO:
        return RED
    if state == QubitState.ONE:
        return BLUE
    return PURPLE


class QubitItem:
    """A qubit particle flowing through the factory."""

    _next_id = 0

    def __init__(self, state=QubitState.ZERO):
        QubitItem._next_id += 1
        self.uid = QubitItem._next_id
        self.progress = 0.0
        self.state = state
        self.phase_flipped = False
        self.entangle_group: int | None = None
        self.is_disappearing = False
        self.disappear_time = 0.0

    # Drawing is handled by rendering.draw_qubit_item() to avoid
    # a circular dependency between entities and sprites.


# ---------------------------------------------------------------------------
# Tile
# ---------------------------------------------------------------------------

class Tile:
    """A single grid tile.  building is a string ID (see gate_registry)."""

    def __init__(self):
        self.building = "empty"             # string gate ID
        self.direction = Direction.RIGHT
        self.item: QubitItem | None = None
        self.control_item: QubitItem | None = None
        self.spawn_timer = 0.0
        self.process_timer = 0.0
        self.measurements = []
        self.measure_flash = 0.0
        self.sink_target: QubitState | None = None
        self.sink_total = 0
        self.sink_match = 0
