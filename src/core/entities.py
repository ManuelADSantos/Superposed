"""Game entities: qubits, tiles, and directions."""

from __future__ import annotations

import math
from enum import Enum

from .config import RED, BLUE, PURPLE, WHITE

_S = 1 / math.sqrt(2)


class Direction(Enum):
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
    _next_id = 0

    def __init__(self, state=QubitState.ZERO):
        QubitItem._next_id += 1
        self.uid = QubitItem._next_id
        self.progress = 0.0
        if state == QubitState.ONE:
            self.alpha, self.beta = 0 + 0j, 1 + 0j
        elif state == QubitState.SUPERPOSITION:
            self.alpha, self.beta = complex(_S), complex(_S)
        else:
            self.alpha, self.beta = 1 + 0j, 0 + 0j
        self.entangle_group: int | None = None
        self.is_disappearing = False
        self.disappear_time = 0.0

    @property
    def state(self) -> QubitState:
        p0 = abs(self.alpha) ** 2
        if p0 > 0.999:
            return QubitState.ZERO
        if p0 < 0.001:
            return QubitState.ONE
        return QubitState.SUPERPOSITION

    @property
    def phase_flipped(self) -> bool:
        if self.state != QubitState.SUPERPOSITION:
            return False
        return (self.alpha.conjugate() * self.beta).real < 0


class Tile:
    def __init__(self):
        self.building = "empty"
        self.direction = Direction.RIGHT
        self.item: QubitItem | None = None
        self.spawn_timer = 0.0
        self.process_timer = 0.0
        self.measurements = []
        self.measure_flash = 0.0
        self.sink_target: QubitState | None = None
        self.sink_total = 0
        self.sink_match = 0
        self.peer: tuple[int, int] | None = None
        self.is_ctrl: bool = False
        self.role: int = 1
