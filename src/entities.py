"""Game entities: qubits, tiles, and building types."""

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
    """90° clockwise."""
    return Direction((d.value + 1) % 4)


def ccw_dir(d: Direction) -> Direction:
    """90° counter-clockwise."""
    return Direction((d.value - 1) % 4)


def dir_from_delta(dx, dy) -> Optional[Direction]:
    """Return Direction for a unit vector, or None."""
    for d, (vx, vy) in DIR_VECTORS.items():
        if (vx, vy) == (dx, dy):
            return d
    return None


# ---------------------------------------------------------------------------
# Building types
# ---------------------------------------------------------------------------

class BuildingType(Enum):
    """Factory building types."""
    EMPTY = 0
    BELT = 1
    GENERATOR = 2
    HADAMARD = 3
    X_GATE = 4
    MEASUREMENT = 5
    Z_GATE = 6
    CNOT = 7
    SPLITTER = 8
    OUTPUT_SINK = 9


# Toolbar order and metadata
BUILDING_INFO = {
    BuildingType.BELT:        {"key": "1", "name": "Belt",        "tip": "Transports qubits"},
    BuildingType.GENERATOR:   {"key": "2", "name": "Generator",   "tip": "Spawns |0⟩ qubits"},
    BuildingType.HADAMARD:    {"key": "3", "name": "Hadamard",    "tip": "Creates superposition"},
    BuildingType.X_GATE:      {"key": "4", "name": "X Gate",      "tip": "Flips |0⟩↔|1⟩"},
    BuildingType.Z_GATE:      {"key": "5", "name": "Z Gate",      "tip": "Phase flip"},
    BuildingType.CNOT:        {"key": "6", "name": "CNOT",        "tip": "Entangles two qubits"},
    BuildingType.MEASUREMENT: {"key": "7", "name": "Measure",     "tip": "Collapses superposition"},
    BuildingType.SPLITTER:    {"key": "8", "name": "Splitter",    "tip": "Routes by state"},
    BuildingType.OUTPUT_SINK: {"key": "9", "name": "Sink",        "tip": "Collects output qubits"},
}

TOOLBAR_ORDER = [
    BuildingType.BELT,
    BuildingType.GENERATOR,
    BuildingType.HADAMARD,
    BuildingType.X_GATE,
    BuildingType.Z_GATE,
    BuildingType.CNOT,
    BuildingType.MEASUREMENT,
    BuildingType.SPLITTER,
    BuildingType.OUTPUT_SINK,
]


# ---------------------------------------------------------------------------
# Qubit
# ---------------------------------------------------------------------------

class QubitState(Enum):
    """Visual / logical quantum states."""
    ZERO = 0
    ONE = 1
    SUPERPOSITION = 2


def state_color(state):
    """Return the display color for a qubit state."""
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
        self.phase_flipped = False  # True = |−⟩ instead of |+⟩
        self.entangle_group: Optional[int] = None  # shared group id
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
    """A single grid tile containing a building and optionally items."""

    def __init__(self):
        self.building = BuildingType.EMPTY
        self.direction = Direction.RIGHT
        self.item: Optional[QubitItem] = None  # main / target slot
        self.control_item: Optional[QubitItem] = None  # CNOT control slot
        self.spawn_timer = 0.0
        self.process_timer = 0.0  # CNOT processing delay
        self.measurements = []
        self.measure_flash = 0.0
        # Output sink stats
        self.sink_target: Optional[QubitState] = None
        self.sink_total = 0
        self.sink_match = 0
