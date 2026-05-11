"""Game entities: qubits, tiles, and building types."""

import pygame
from enum import Enum
from typing import Optional

from config import RED, BLUE, PURPLE, WHITE


class Direction(Enum):
    """Cardinal directions."""
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


class BuildingType(Enum):
    """Factory building types."""
    EMPTY = 0
    BELT = 1
    GENERATOR = 2
    HADAMARD = 3
    X_GATE = 4
    MEASUREMENT = 5


class QubitState(Enum):
    """Quantum states of a qubit."""
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

    def __init__(self, state=QubitState.ZERO):
        self.progress = 0.0
        self.state = state
        self.is_disappearing = False
        self.disappear_time = 0.0

    def draw(self, surface, x, y, size):
        """Draw the qubit on the given surface."""
        cx = x + size // 2
        cy = y + size // 2

        # Calculate animation state if disappearing
        if self.is_disappearing:
            scale = max(0.1, self.disappear_time / 0.3)  # Shrink to 0.1 size over 0.3s
        else:
            scale = 1.0

        # Draw circle with scale
        if self.state == QubitState.SUPERPOSITION:
            pygame.draw.circle(surface, PURPLE, (cx, cy), max(2, int(size * scale / 4)))
            pygame.draw.circle(surface, WHITE, (cx, cy), max(2, int(size * scale / 4)), 2)
        else:
            pygame.draw.circle(surface, state_color(self.state), (cx, cy), max(2, int(size * scale / 5)))


class Tile:
    """A single grid tile containing a building and optionally an item."""

    def __init__(self):
        self.building = BuildingType.EMPTY
        self.direction = Direction.RIGHT
        self.item: Optional[QubitItem] = None
        self.spawn_timer = 0
        self.measurements = []
        self.measure_flash = 0.0
