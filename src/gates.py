"""Quantum gate transformations and measurement."""

import random

from entities import BuildingType, QubitState


def transform_qubit(building, item):
    """Apply a gate transformation to a qubit."""
    if building == BuildingType.HADAMARD:
        if item.state in (QubitState.ZERO, QubitState.ONE):
            item.state = QubitState.SUPERPOSITION
        else:
            item.state = random.choice([QubitState.ZERO, QubitState.ONE])
    elif building == BuildingType.X_GATE:
        if item.state == QubitState.ZERO:
            item.state = QubitState.ONE
        elif item.state == QubitState.ONE:
            item.state = QubitState.ZERO
    elif building == BuildingType.MEASUREMENT:
        if item.state == QubitState.SUPERPOSITION:
            item.state = random.choice([QubitState.ZERO, QubitState.ONE])
        return item.state


def record_measurement(tile, outcome):
    """Record the outcome of a measurement on a tile."""
    tile.measurements.append(outcome)
    if len(tile.measurements) > 12:
        tile.measurements.pop(0)
    tile.measure_flash = 0.35
