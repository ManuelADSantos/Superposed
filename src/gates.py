"""Quantum gate transformations, measurement, and entanglement."""

import random

from entities import BuildingType, QubitState, QubitItem
from world import (
    create_entangle_group, register_entangled,
    get_entangled_partners, break_entanglement,
)


# ---------------------------------------------------------------------------
# Single-qubit gates
# ---------------------------------------------------------------------------

def apply_hadamard(item: QubitItem):
    """H gate: |0⟩/|1⟩ → superposition, superposition → basis state.

    If phase_flipped (i.e. |−⟩), H gives |1⟩ deterministically.
    Otherwise (|+⟩), H gives |0⟩ deterministically.
    This makes H→Z→H = X  (a key interference insight).
    """
    if item.state in (QubitState.ZERO, QubitState.ONE):
        item.phase_flipped = (item.state == QubitState.ONE)
        item.state = QubitState.SUPERPOSITION
    else:
        # Superposition → basis state via interference
        if item.phase_flipped:
            item.state = QubitState.ONE    # H|−⟩ = |1⟩
        else:
            item.state = QubitState.ZERO   # H|+⟩ = |0⟩
        item.phase_flipped = False
        break_entanglement(item)


def apply_x(item: QubitItem):
    """X (NOT) gate: flips |0⟩↔|1⟩; superposition unchanged."""
    if item.state == QubitState.ZERO:
        item.state = QubitState.ONE
    elif item.state == QubitState.ONE:
        item.state = QubitState.ZERO
    # superposition: X|+⟩ = |+⟩ (unchanged in this simplified model)


def apply_z(item: QubitItem):
    """Z gate: phase flip.  Toggles the phase flag on superposition qubits.

    |0⟩ → |0⟩  (no visible change)
    |1⟩ → |1⟩  (phase is global, invisible on basis states)
    |+⟩ → |−⟩  (flips phase_flipped flag; next H → |1⟩)
    |−⟩ → |+⟩  (flips back; next H → |0⟩)
    """
    if item.state == QubitState.SUPERPOSITION:
        item.phase_flipped = not item.phase_flipped


# ---------------------------------------------------------------------------
# Two-qubit gate: CNOT
# ---------------------------------------------------------------------------

def apply_cnot(control: QubitItem, target: QubitItem):
    """CNOT: if control is |1⟩ flip target; if superposition, entangle."""
    if control.state == QubitState.ONE:
        apply_x(target)
    elif control.state == QubitState.SUPERPOSITION:
        if target.state == QubitState.ZERO:
            # |+⟩|0⟩  →  Bell state  (both become entangled superposition)
            target.state = QubitState.SUPERPOSITION
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)
        elif target.state == QubitState.ONE:
            # |+⟩|1⟩  →  entangled, anti-correlated
            target.state = QubitState.SUPERPOSITION
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)
    # control |0⟩  →  target unchanged


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def measure_qubit(item: QubitItem) -> QubitState:
    """Collapse a qubit.  Entangled partners collapse too.

    Measurement is always probabilistic — phase doesn't affect
    measurement probabilities in the computational basis.
    """
    if item.state == QubitState.SUPERPOSITION:
        result = random.choice([QubitState.ZERO, QubitState.ONE])
        item.state = result
        item.phase_flipped = False
        # Collapse entangled partners to the *same* outcome (Bell |Φ+⟩)
        for partner in get_entangled_partners(item):
            if partner.state == QubitState.SUPERPOSITION:
                partner.state = result
                partner.phase_flipped = False
            break_entanglement(partner)
        break_entanglement(item)
    return item.state


# ---------------------------------------------------------------------------
# Dispatcher used by simulation
# ---------------------------------------------------------------------------

def transform_qubit(building: BuildingType, item: QubitItem):
    """Apply a single-qubit gate.  Returns measurement outcome or None."""
    if building == BuildingType.HADAMARD:
        apply_hadamard(item)
    elif building == BuildingType.X_GATE:
        apply_x(item)
    elif building == BuildingType.Z_GATE:
        apply_z(item)
    elif building == BuildingType.MEASUREMENT:
        outcome = measure_qubit(item)
        return outcome
    return None


def record_measurement(tile, outcome):
    """Record a measurement result on a tile for the histogram."""
    tile.measurements.append(outcome)
    if len(tile.measurements) > 20:
        tile.measurements.pop(0)
    tile.measure_flash = 0.35
