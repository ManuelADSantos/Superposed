"""Export the current grid layout as a Qiskit QuantumCircuit Python script."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime

from ..core.entities import Direction, DIR_VECTORS
from ..core import world as _world_module
from .gate_registry import get_gate, Category, BELT, GENERATOR, OUTPUT_SINK, EMPTY


@dataclass
class PathStep:
    x: int
    y: int
    building: str
    role: str | None = None


_SINGLE_MAP = {
    "hadamard":  "h",
    "x_gate":    "x",
    "y_gate":    "y",
    "z_gate":    "z",
}

_TWO_QUBIT_MAP = {
    "cnot": "cx",
    "cz": "cz",
    "swap": "swap",
    "toffoli": "ccx",
}


def _find_generators(grid: dict) -> list[tuple[int, int, Direction]]:
    gens = []
    for (x, y), tile in grid.items():
        if tile.building == GENERATOR:
            gens.append((x, y, tile.direction))
    gens.sort(key=lambda g: (g[1], g[0]))
    return gens


def _trace_path(start_x: int, start_y: int, start_dir: Direction,
                grid: dict) -> list[PathStep]:
    path: list[PathStep] = []
    x, y = start_x, start_y
    direction = start_dir
    visited: set[tuple[int, int]] = {(x, y)}

    while True:
        dx, dy = DIR_VECTORS[direction]
        nx, ny = x + dx, y + dy

        if (nx, ny) in visited:
            break

        tile = grid.get((nx, ny))
        if tile is None or tile.building == EMPTY:
            break

        visited.add((nx, ny))
        bid = tile.building
        gate = get_gate(bid)

        if bid == BELT or bid == GENERATOR:
            direction = tile.direction
            x, y = nx, ny
            continue

        if bid == OUTPUT_SINK:
            path.append(PathStep(nx, ny, OUTPUT_SINK))
            break

        if gate and gate.category == Category.SINGLE:
            path.append(PathStep(nx, ny, bid))
            direction = tile.direction
            x, y = nx, ny
            continue

        if gate and gate.category == Category.CONSUMER:
            path.append(PathStep(nx, ny, bid))
            break

        if gate and gate.category == Category.ROUTER:
            path.append(PathStep(nx, ny, bid))
            break

        if gate and gate.category == Category.TWO_QUBIT:
            # Multi-qubit gate roles share the primary tile position so
            # _build_pair_map matches the controls and target.
            if not tile.peer:
                break
            px, py = tile.peer if tile.is_ctrl else (nx, ny)
            role_num = getattr(tile, "role", 1)
            if tile.is_ctrl and role_num == 1:
                role_num = 2
            role = "target" if role_num == 1 else f"control{role_num - 1}"
            if gate.qubits == 2 and role != "target":
                role = "control"
            path.append(PathStep(px, py, bid, role=role))
            direction = tile.direction
            x, y = nx, ny
            continue

        break

    return path


def _build_pair_map(all_paths: list[list[PathStep]]
                    ) -> dict[tuple[int, int], dict[str, int]]:
    pair_map: dict[tuple[int, int], dict[str, int]] = {}
    for qi, path in enumerate(all_paths):
        for step in path:
            if step.role is not None:
                pos = (step.x, step.y)
                pair_map.setdefault(pos, {})
                pair_map[pos][step.role] = qi
    return pair_map


def generate_qiskit_script(grid: dict | None = None) -> str:
    if grid is None:
        grid = _world_module.world

    generators = _find_generators(grid)
    if not generators:
        return (
            "# Superposed — Qiskit Export\n"
            "# No generators found in the current layout.\n"
        )

    all_paths = [_trace_path(gx, gy, gdir, grid)
                 for gx, gy, gdir in generators]

    pair_map = _build_pair_map(all_paths)

    has_measure = any(
        step.building in ("measurement", "splitter")
        for path in all_paths
        for step in path
    )

    n_qubits = len(generators)
    n_classical = n_qubits if has_measure else 0
    classical_idx = 0

    ops: list[str] = []
    emitted_pairs: set[tuple[int, int]] = set()
    warnings: list[str] = []

    for qi, path in enumerate(all_paths):
        if not path:
            ops.append(f"# q{qi}: no gates encountered")
            continue

        ops.append(f"# q{qi}: generator at "
                   f"({generators[qi][0]}, {generators[qi][1]})")

        for step in path:
            if step.role is not None:
                pos = (step.x, step.y)
                if pos not in emitted_pairs:
                    pair = pair_map.get(pos, {})
                    tgt = pair.get("target")
                    method = _TWO_QUBIT_MAP.get(step.building, "cx")
                    if method == "ccx":
                        ctrl1 = pair.get("control1")
                        ctrl2 = pair.get("control2")
                        if ctrl1 is not None and ctrl2 is not None and tgt is not None:
                            ops.append(f"qc.ccx({ctrl1}, {ctrl2}, {tgt})")
                            emitted_pairs.add(pos)
                        else:
                            warnings.append(
                                f"# WARNING: {step.building} at ({pos[0]},{pos[1]}) "
                                "missing input — skipped"
                            )
                    else:
                        ctrl = pair.get("control")
                        if ctrl is not None and tgt is not None:
                            ops.append(f"qc.{method}({ctrl}, {tgt})")
                            emitted_pairs.add(pos)
                        else:
                            missing = "target" if tgt is None else "control"
                            warnings.append(
                                f"# WARNING: {step.building} at ({pos[0]},{pos[1]}) "
                                f"missing {missing} input — skipped"
                            )

            elif step.building in _SINGLE_MAP:
                method = _SINGLE_MAP[step.building]
                ops.append(f"qc.{method}({qi})")

            elif step.building in ("measurement", "splitter"):
                ops.append(f"qc.measure({qi}, {classical_idx})")
                classical_idx += 1
                if step.building == "splitter":
                    ops.append(
                        f"# Splitter at ({step.x},{step.y}): "
                        f"|0> goes straight, |1> turns CW"
                    )

            elif step.building == OUTPUT_SINK:
                ops.append(f"# -> output sink at ({step.x},{step.y})")

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


def export_circuit(directory: str | None = None) -> str:
    script = generate_qiskit_script()

    if directory is None:
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
