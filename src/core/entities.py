"""Game entities: qubits, tiles, and directions."""

from __future__ import annotations

import math
from enum import Enum

from .config import RED, BLUE, PURPLE

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
    PLUS = 2       # |+⟩ = (|0⟩+|1⟩)/√2
    MINUS = 3      # |−⟩ = (|0⟩−|1⟩)/√2
    PLUS_I = 4     # |i⟩ = (|0⟩+i|1⟩)/√2
    MINUS_I = 5    # |−i⟩ = (|0⟩−i|1⟩)/√2


def state_color(state):
    if state == QubitState.ZERO:
        return RED
    if state == QubitState.ONE:
        return BLUE
    return PURPLE  # ponytail: all supers purple, per-state colors if visual distinction needed


class QubitItem:
    _next_id = 0

    def __init__(self, state=QubitState.ZERO):
        QubitItem._next_id += 1
        self.uid = QubitItem._next_id
        self.progress = 0.0
        if state == QubitState.ONE:
            self.alpha, self.beta = 0 + 0j, 1 + 0j
        elif state == QubitState.PLUS:
            self.alpha, self.beta = complex(_S), complex(_S)
        elif state == QubitState.MINUS:
            self.alpha, self.beta = complex(_S), complex(-_S)
        elif state == QubitState.PLUS_I:
            self.alpha, self.beta = complex(_S), complex(0, _S)
        elif state == QubitState.MINUS_I:
            self.alpha, self.beta = complex(_S), complex(0, -_S)
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
        c = self.alpha.conjugate() * self.beta
        q = round(math.atan2(c.imag, c.real) / (math.pi / 2)) % 4
        return (QubitState.PLUS, QubitState.PLUS_I, QubitState.MINUS, QubitState.MINUS_I)[q]

    @property
    def phase_angle(self) -> float:
        if self.state not in (QubitState.ZERO, QubitState.ONE):
            c = self.alpha.conjugate() * self.beta
            return math.atan2(c.imag, c.real)
        amp = self.beta if abs(self.alpha) < abs(self.beta) else self.alpha
        return math.atan2(amp.imag, amp.real) if abs(amp) > 1e-10 else 0.0

    @property
    def phase_flipped(self) -> bool:
        if self.state in (QubitState.ZERO, QubitState.ONE):
            return False
        return math.cos(self.phase_angle) < -1e-6

    @property
    def bloch(self) -> tuple[float, float, float]:
        norm = abs(self.alpha) ** 2 + abs(self.beta) ** 2
        if norm <= 1e-20:
            return (0.0, 0.0, 1.0)
        coherence = self.alpha.conjugate() * self.beta
        return (
            2 * coherence.real / norm,
            2 * coherence.imag / norm,
            (abs(self.alpha) ** 2 - abs(self.beta) ** 2) / norm,
        )


class Tile:
    def __init__(self):
        self.building = "empty"
        self.direction = Direction.RIGHT
        self.item: QubitItem | None = None
        self.spawn_timer = 0.0
        self.spawn_state: QubitState | None = None
        self.spawn_phase: float | None = None
        self.process_timer = 0.0
        self.measurements = []
        self.measure_flash = 0.0
        self.sink_target: QubitState | None = None
        self.sink_phase: float | None = None
        self.sink_total = 0
        self.sink_match = 0
        self.peer: tuple[int, int] | None = None
        self.is_ctrl: bool = False
        self.role: int = 1
