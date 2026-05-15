"""Game entities: qubits, tiles, and directions.

Building types are now string IDs managed by gate_registry.
"""

import pygame
from enum import Enum
from typing import Optional

from config import RED, BLUE, PURPLE, WHITE


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


def dir_from_delta(dx, dy) -> Optional[Direction]:
    for d, (vx, vy) in DIR_VECTORS.items():
        if (vx, vy) == (dx, dy):
            return d
    return None


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
        self.entangle_group: Optional[int] = None
        self.is_disappearing = False
        self.disappear_time = 0.0

    def draw(self, surface, x, y, size):
        from sprites import get_qubit_sprite
        if self.is_disappearing:
            scale = max(0.18, self.disappear_time / 0.3)
        else:
            scale = 1.0
        sprite_size = max(8, int(size * scale))
        sprite = get_qubit_sprite(self.state, sprite_size,
                                  self.is_disappearing, scale,
                                  self.entangle_group is not None)
        sprite_rect = sprite.get_rect(center=(x + size // 2, y + size // 2))
        surface.blit(sprite, sprite_rect)


# ---------------------------------------------------------------------------
# Tile
# ---------------------------------------------------------------------------

class Tile:
    """A single grid tile.  building is a string ID (see gate_registry)."""

    def __init__(self):
        self.building = "empty"             # string gate ID
        self.direction = Direction.RIGHT
        self.item: Optional[QubitItem] = None
        self.control_item: Optional[QubitItem] = None
        self.spawn_timer = 0.0
        self.process_timer = 0.0
        self.measurements = []
        self.measure_flash = 0.0
        self.sink_target: Optional[QubitState] = None
        self.sink_total = 0
        self.sink_match = 0
