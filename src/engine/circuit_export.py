"""Export the current grid layout as a Qiskit QuantumCircuit Python script.

Algorithm:
  1. Find all generators in the grid (each = one qubit line).
  2. Trace each qubit's path through belts and gates.
  3. Match CNOT control/target pairs across paths.
  4. Emit a .py script that constructs the equivalent QuantumCircuit.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime

from ..core.entities import Direction, DIR_VECTORS, opposite_dir, cw_dir, ccw_dir
from ..core import world as _world_module
from .gate_registry import get_gate, Category, BELT, GENERATOR, OUTPUT_SINK, EMPTY


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class PathStep:
    """A single gate encountered along a qubit's path."""
    x: int
    y: int
    building: str
    role: str | None = None          # "control" or "target" (CNOT only)


# ── Gate ID → Qiskit method mapping ──────────────────────────────────────────

_SINGLE_MAP = {
    "hadamard":  "h",
    "x_gate":    "x",
    "z_gate":    "z",
}


# ── Phase 1: find generators ────────────────────────────────────────────────

def _find_generators(grid: dict) -> list[tuple[int, int, Direction]]:
    """Return all generators sorted top-to-bottom, left-to-right."""
    gens = []
    for (x, y), tile in grid.items():
        if tile.building == GENERATOR:
            gens.append((x, y, tile.direction))
    gens.sort(key=lambda g: (g[1], g[0]))
    return gens


# ── Phase 2: trace a single qubit path ─────────────────────────────────────

def _trace_path(start_x: int, start_y: int, start_dir: Direction,
                grid: dict) -> list[PathStep]:
    """Follow a qubit from *start* through belts and gates.

    Mirrors the movement logic in simulation.py — belts change direction,
    gates are recorded, consumers/routers/sinks terminate the path.
    """
    path: list[PathStep] = []
    x, y = start_x, start_y
    direction = start_dir
    visited: set[tuple[int, int]] = {(x, y)}

    while True:
        dx, dy = DIR_VECTORS[direction]
        nx, ny = x + dx, y + dy

        # Loop detection
        if (nx, ny) in visited:
            break

        tile = grid.get((nx, ny))
        if tile is None or tile.building == EMPTY:
            break

        visited.add((nx, ny))
        bid = tile.building
        gate = get_gate(bid)

        # Infrastructure: belt / generator — just transport
        if bid == BELT or bid == GENERATOR:
            direction = tile.direction
            x, y = nx, ny
            continue

        # Output sink — path terminates
        if bid == OUTPUT_SINK:
            path.append(PathStep(nx, ny, OUTPUT_SINK))
            break

        # Single-qubit gate
        if gate and gate.category == Category.SINGLE:
            path.append(PathStep(nx, ny, bid))
            direction = tile.direction
            x, y = nx, ny
            continue

        # Consumer (measurement) — terminates path
        if gate and gate.category == Category.CONSUMER:
            path.append(PathStep(nx, ny, bid))
            break

        # Router (splitter) — acts as measure + routing, terminates
        if gate and gate.category == Category.ROUTER:
            path.append(PathStep(nx, ny, bid))
            break

        # Two-qubit gate (CNOT)
        if gate and gate.category == Category.TWO_QUBIT:
            arrival = opposite_dir(direction)
            target_input = opposite_dir(tile.direction)
            control_input = ccw_dir(tile.direction)

            if arrival == target_input:
                role = "target"
            elif arrival == control_input:
                role = "control"
            else:
                break  # invalid approach — qubit would vanish

            path.append(PathStep(nx, ny, bid, role=role))

            # Exit directions mirror simulation._process_two_qubit:
            #   target exits in tile.direction
            #   control exits CW from tile.direction
            if role == "target":
                direction = tile.direction
            else:
                direction = cw_dir(tile.direction)
            x, y = nx, ny
            continue

        # Unknown building — stop
        break

    return path


# ── Phase 3: resolve CNOT pairs ────────────────────────────────────────────

def _build_cnot_map(all_paths: list[list[PathStep]]
                    ) -> dict[tuple[int, int], dict[str, int]]:
    """Map each CNOT tile position to its control and target qubit indices."""
    cnot_map: dict[tuple[int, int], dict[str, int]] = {}
    for qi, path in enumerate(all_paths):
        for step in path:
            if step.role is not None:                       # CNOT step
                pos = (step.x, step.y)
                cnot_map.setdefault(pos, {})
                cnot_map[pos][step.role] = qi
    return cnot_map


# ── Phase 4: generate Qiskit script ────────────────────────────────────────

def generate_qiskit_script(grid: dict | None = None) -> str:
    """Return a complete Qiskit Python script as a string.

    If *grid* is ``None``, uses the current world state.
    """
    if grid is None:
        grid = _world_module.world

    generators = _find_generators(grid)
    if not generators:
        return (
            "# Superposed — Qiskit Export\n"
            "# No generators found in the current layout.\n"
        )

    # Trace paths
    all_paths = [_trace_path(gx, gy, gdir, grid)
                 for gx, gy, gdir in generators]

    # Resolve CNOT pairs
    cnot_map = _build_cnot_map(all_paths)

    # Determine if we need classical bits
    has_measure = any(
        step.building in ("measurement", "splitter")
        for path in all_paths
        for step in path
    )

    n_qubits = len(generators)
    n_classical = n_qubits if has_measure else 0
    classical_idx = 0  # running counter for classical bits

    # Build operation lines
    ops: list[str] = []
    emitted_cnots: set[tuple[int, int]] = set()
    warnings: list[str] = []

    for qi, path in enumerate(all_paths):
        if not path:
            ops.append(f"# q{qi}: no gates encountered")
            continue

        ops.append(f"# q{qi}: generator at "
                   f"({generators[qi][0]}, {generators[qi][1]})")

        for step in path:
            # Single-qubit gate
            if step.building in _SINGLE_MAP:
                method = _SINGLE_MAP[step.building]
                ops.append(f"qc.{method}({qi})")

            # CNOT
            elif step.role is not None:
                pos = (step.x, step.y)
                if pos not in emitted_cnots:
                    pair = cnot_map.get(pos, {})
                    ctrl = pair.get("control")
                    tgt = pair.get("target")
                    if ctrl is not None and tgt is not None:
                        ops.append(f"qc.cx({ctrl}, {tgt})")
                        emitted_cnots.add(pos)
                    else:
                        missing = "target" if tgt is None else "control"
                        warnings.append(
                            f"# WARNING: CNOT at ({pos[0]},{pos[1]}) "
                            f"missing {missing} input — skipped"
                        )

            # Measurement / splitter
            elif step.building in ("measurement", "splitter"):
                ops.append(f"qc.measure({qi}, {classical_idx})")
                classical_idx += 1
                if step.building == "splitter":
                    ops.append(
                        f"# Splitter at ({step.x},{step.y}): "
                        f"|0> goes straight, |1> turns CW"
                    )

            # Sink — informational
            elif step.building == OUTPUT_SINK:
                ops.append(f"# → output sink at ({step.x},{step.y})")

    # ── Assemble the script ──────────────────────────────────────────────
    header = [
        '"""Qiskit circuit exported from Superposed.',
        f'   Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'   Qubits: {n_qubits}',
        '"""',
        "",
        "from qiskit import QuantumCircuit",
        "",
    ]

    if has_measure:
        header.append(f"qc = QuantumCircuit({n_qubits}, {n_classical})")
    else:
        header.append(f"qc = QuantumCircuit({n_qubits})")

    header.append("")

    footer = [
        "",
        "# Draw the circuit",
        "print(qc.draw())",
    ]

    lines = header + warnings + ops + footer
    return "\n".join(lines) + "\n"


# ── Public API ──────────────────────────────────────────────────────────────

def export_circuit(directory: str | None = None) -> str:
    """Write the Qiskit script to a file and return the file path.

    The file is saved next to the game directory by default, or to
    *directory* if specified.
    """
    script = generate_qiskit_script()

    if directory is None:
        # Default: same folder that contains the src/ package
        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "exports",
        )

    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"circuit_{timestamp}.py"
    filepath = os.path.join(directory, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(script)

    return filepath
