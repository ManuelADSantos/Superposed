# Architecture

This document describes the internal design of Superposed: how the modules fit together, what patterns are used, and the reasoning behind the key decisions.

## Overview

Superposed is a single-threaded pygame application structured as a proper Python package under `src/`. The package is split into four subpackages, each with a clear responsibility:

| Subpackage | Role | Key files |
|---|---|---|
| `core/` | Data model and shared state | config, entities, world |
| `engine/` | Simulation logic and gate definitions | gate_registry, simulation, gates/ |
| `ui/` | Everything the player sees and touches | rendering, sprites, menu, input_handler |
| `content/` | Game content that designers edit | levels |

The dependency flow is strictly top-down: `main.py` imports from all four subpackages, `engine/` and `ui/` import from `core/`, and `content/` imports entity types from `core/` and gate IDs from `engine/`. There are no circular dependencies.

The current campaign is organized into 15 chapters and 37 levels. Chapter concepts are shown on the level list, and starting a level loads play immediately with the briefing overlay visible.

## Entry Points

There are three ways to start the game, and all of them call the same `main()` function in `src/main.py`:

1. `python run.py` — direct script execution, imports `src.main`.
2. `python -m src` — package execution via `__main__.py`, uses a relative import.
3. `superposed` — CLI command after `pip install -e .`, configured in `pyproject.toml`.

## Game Loop and State Machine

`main.py` runs the game loop with a state machine driven by the `GameState` enum (defined in `ui/menu.py`). The states are:

```
MAIN_MENU → CHAPTER_SELECT → LEVEL_SELECT → LEVEL_PLAY → WIN_SCREEN
MAIN_MENU → SANDBOX
```

Each frame follows the same sequence: process input, update simulation (if not paused), render everything. The state determines which input handler and renderer are active — for example, `MAIN_MENU` only draws the menu and listens for button clicks, while `LEVEL_PLAY` runs the full simulation loop.

## Core Subpackage

### config.py

Flat module of constants: window size, tile size, physics speeds, UI dimensions, and the colour palette. `WIDTH` and `HEIGHT` are mutable — `main.py` overwrites them after creating the pygame window to support different screen sizes.

### entities.py

Defines the fundamental data types:

**Direction** — enum with UP, RIGHT, DOWN, LEFT and helper functions for rotation (`cw_dir`, `ccw_dir`, `opposite_dir`) and delta conversion.

**QubitState** — enum with ZERO, ONE, SUPERPOSITION. The `state_color()` function maps these to red, blue, and purple respectively.

**QubitItem** — a qubit particle flowing through the factory. Tracks its amplitudes (`alpha`, `beta`), derived display state/phase, entanglement group, progress along the current tile, and disappearance animation state. Each instance gets a unique `uid` from a counter.

**Tile** — a single grid cell. Holds the building ID (a string like `"hadamard"`), direction, the qubit currently on it, optional peer metadata for two-cell gates, generator spawn state/phase, process timers, measurement histogram, and sink output counters.

### world.py

All mutable game state lives in the `WorldState` class: the sparse grid (a `dict` mapping `(x, y)` to `Tile`), camera position and zoom, entanglement tracking, and the current level definition.

The entanglement registry is a pair of structures: `entangle_groups` maps a group ID to an `EntangleGroup` (`qubit_order` plus joint `statevec`), and `entangle_lookup` maps each qubit UID to its live `QubitItem`. This keeps partner lookup simple while allowing two-qubit gates to operate on entangled groups.

Module-level proxy variables (`world`, `locked_tiles`, `available_buildings`, etc.) are re-bound to the live `WorldState` on reset/load via `_sync_from_state()`, so `import world as W; W.world` always resolves to the current dict.

**Key functions:**
- `reset_world()` — reinitialises all state, clears sprite caches.
- `load_level(level_def, index)` — places pre-built tiles, sets locked positions, configures camera.
- `check_win_condition()` — returns True when every sink has met its target count.

## Engine Subpackage

### gate_registry.py

The central registry is a dictionary mapping string IDs to `GateDef` dataclass instances. Each `GateDef` carries the gate's metadata (name, tooltip, colour), its `category` (which determines how the simulation calls it), its `transform` function, and an optional overlay callback.

**Categories and their transform signatures:**

| Category | Signature | When called |
|---|---|---|
| INFRASTRUCTURE | — | Hardcoded in simulation (belt movement, spawning, collecting) |
| SINGLE | `transform(item)` | When a qubit arrives at the gate tile |
| TWO_QUBIT | `transform(*controls, target)` | When all multi-qubit slots are occupied |
| CONSUMER | `transform(item, tile)` | Qubit is consumed (measurement records to tile) |
| ROUTER | `transform(x, y, tile, item, eject_fn)` | Gate controls where the qubit goes next |

**Auto-loader:** `load_gates()` scans the `gates/` directory, imports every `.py` file in sorted order, and each file calls `register()` at module scope. This means adding a new gate is a single-file operation with zero changes to existing code.

**Toolbar:** `active_toolbar(available)` filters the full registry to only the gates allowed in the current level, preserving the `order` field for consistent toolbar layout.

### simulation.py

`update_items(dt)` is the physics loop, called once per frame. It iterates every tile in the world and:

1. **Advances progress** — qubits on belts move forward by `BELT_SPEED * dt`. When progress reaches 1.0, the qubit is ready to transfer.
2. **Spawns qubits** — generator tiles create new `QubitItem`s at a fixed rate, defaulting to `|0>` unless the level config sets a spawn state.
3. **Processes two-qubit gates** — the primary tile waits for its control-dot peer and target tile to fill (with a short delay for visual clarity), then calls the gate's transform and ejects both qubits.
4. **Applies single-qubit gates** — when a qubit arrives (progress crosses 0.0), the gate's transform is called immediately.
5. **Transfers qubits** — when a qubit finishes a tile, it moves to the next tile in the facing direction. If the next tile doesn't exist or is full, the qubit starts a disappearance animation.

`_safe_transform(gate, *args)` wraps every gate call in a try/except so a buggy gate definition can never crash the game — it prints to stderr and leaves the qubit unmodified.

**Multi-qubit routing:** CNOT/CZ/SWAP occupy two parallel cells; Toffoli occupies three. Companion tiles sit counter-clockwise from the primary/target lane. All lanes flow in the gate direction.

### gates/

Each gate file follows the same pattern: define a `_transform` function, then call `register()` with a `GateDef`. The files are:

- **_infrastructure.py** — Belt, Generator, Output Sink. These have no transform; simulation handles them directly.
- **hadamard.py** — Applies the Hadamard matrix, creating or interfering superposition.
- **x_gate.py** — Pauli-X / NOT gate.
- **y_gate.py** — Pauli-Y gate, including complex phase.
- **z_gate.py** — Phase gate.
- **cnot.py** — Two-qubit controlled NOT via the world's state-vector helpers.
- **cz.py** — Two-qubit controlled phase flip with phase kickback.
- **toffoli.py** — Three-qubit controlled-controlled NOT.
- **measurement.py** — Consumer gate. Collapses superposition to `|0>` or `|1>` with 50/50 probability. Collapses entangled partners to the same state. Records results in a tile-level histogram (capped at 20 entries). Includes an overlay function that draws the histogram directly on the tile.
- **splitter.py** — Router gate. Implicitly measures the qubit, then routes `|0>` straight ahead and `|1>` clockwise. Used to separate qubit states spatially.
- **swap.py** — Two-qubit gate that exchanges two qubit states.
- **noise.py** — Randomly applies an X error.

## UI Subpackage

### rendering.py

Draws the grid, buildings, qubits, toolbar, HUD, level progress, and ghost previews. Two-cell gates also draw a connecting line between the primary tile and its control-dot companion (`_draw_peer_link`). Key functions:

- `draw_grid()` — iterates visible tiles and blits cached building sprites with directional rotation. Draws qubit particles on top with glow effects.
- `draw_qubit_item()` — standalone function that renders a qubit with state colour, entanglement halo, and fade-out animation. Extracted to its own function to avoid circular imports.
- `draw_toolbar()` — renders the bottom toolbar with building buttons, speed/pause controls, export, and help.
- `draw_level_hud()` — shows level name, objective text, and a progress bar for sink completion.

### sprites.py

Sprite generation follows a three-tier resolution chain:

1. **Custom PNG** — looks for `assets/gates_sprites/<gate_id>.png` or role-specific files such as `cnot_1.png`, then rotates it to match the gate's direction.
2. **Generic fallback** — draws a coloured rounded rectangle with the gate's initial.

All sprites are cached via `@lru_cache`. The caches are cleared on `reset_world()` to handle resolution changes.

### menu.py

Implements the menu flow as draw/handle function pairs:

- **Main menu** — title, subtitle, three buttons (Campaign, Sandbox, Exit), version number in the corner.
- **Chapter select** — chapter cards plus campaign progress overview.
- **Level select** — chapter concept, level cards, and completion badges (stored in a module-level `completed_levels` set).
- **Win screen** — overlay after completing a level, with CHAPTERS and NEXT buttons.

### input_handler.py

Translates pygame events into game actions. Returns an updated `(run_ok, selected_building, selected_rotation, paused, step_requested, back_to_menu)` tuple each frame. Handles camera panning (WASD), recentering (X), zoom (scroll wheel), building placement (left click), removal (right click), rotation (R), briefing toggle (F), and toolbar selection (number keys or clicking toolbar buttons). Placing a two-qubit gate auto-creates its control-dot companion one cell counter-clockwise; deleting either half removes both. Dragging with the belt selected lays a continuous run of belts that follow the cursor.

## Content Subpackage

### levels.py

Thirty-seven tutorial levels across 15 chapters, flattened into `ALL_LEVELS` from the per-chapter lists in `CHAPTERS`. Each level is a dictionary with:

- `name`, `description`, `briefing` — text shown to the player.
- `pre_placed` — dict mapping `(x, y)` to a `(building_id, direction, param)` tuple for tiles the level starts with. For sinks, `param` is the desired output state or `(state, phase)`. For generators, `param` is the spawn state or `(state, phase)`. Companions for two-qubit gates are generated automatically at load time.
- `locked` — set of `(x, y)` coordinates the player cannot modify.
- `available` — list of gate IDs the player can use (restricts the toolbar).
- `gate_limits` — optional per-level caps for specific gates.
- `win_count` — how many qubits the sink must collect to complete the level.
- `camera` — initial camera position.

The chapters progress through the concepts in order:

1. **Classical Foundations** — belt routing and the X (NOT) gate.
2. **Superposition** — the H gate and purple `|+>` particles.
3. **Measurement** — collapse to a `|0>`/`|1>` histogram.
4. **Phase & Interference** — Z gate; H–Z–H gives deterministic `|1>`.
5. **Entanglement** — CNOT creates correlated Bell pairs.
6. **Multi-Qubit Ops** — CZ and SWAP.
7. **Interference Patterns** — combining phase and superposition.
8. **Quantum Circuits** — multi-gate layouts and the Splitter router.
9. **Quantum Noise** — the noise gate perturbs qubits.
10. **Error Detection** — spotting and correcting corrupted qubits.
11. **Deutsch's Problem** — constant and balanced functions built from basic gates.
12. **Quantum Cloning** — CNOT copies known basis states; no-cloning limits unknown states.
13. **Grand Challenge** — combined multi-concept puzzles.
14. **Quantum Mastery** — capstone levels.
15. **Algorithms** — QFT, Grover, teleportation, and Shor-inspired circuits built from smaller gates.

The full chapter/level data lives in `CHAPTERS` in `levels.py`; this list is the high-level map.

## Design Decisions

### Sparse grid over 2D array

The world is a `dict[(int, int), Tile]` rather than a fixed-size 2D array. This means the sandbox mode has an effectively infinite canvas, tiles only consume memory when placed, and coordinate math stays simple (no bounds checking on the grid itself, only on the viewport).

### String IDs over enum for gates

Gates are identified by string keys (`"hadamard"`, `"belt"`) rather than an enum. This allows new gates to be added without modifying any central type definition — the registry is the only source of truth, and it's populated dynamically at import time.

### Small state vectors over a full simulator

The game stores a two-amplitude state on each solo qubit and a joint state vector only for entangled groups. This is enough to model H, X, Y, Z, CNOT, CZ, SWAP, measurement, and interference without pulling in a full quantum simulation dependency.

### Category-based dispatch

Rather than one giant if/elif chain in the simulation, gates declare their category and the simulation uses it to decide the calling convention. This keeps the simulation loop clean and makes the contract for each gate type explicit.

### Module-level world proxies

The `WorldState` class is the canonical state container, but module-level variables in `world.py` (like `world`, `camera_x`, `zoom`) provide convenient shorthand throughout the codebase. A pair of sync functions keeps them consistent. This avoids passing the state object through every function signature while still having a single place to reset everything.

## Test Coverage

The test suite (`tests/test_gates.py`) covers:

- Core gate transforms (X, H, Z, CNOT, CZ, SWAP, Toffoli, Measurement, Splitter) with basis states and superposition.
- Double-application identity checks (X-X, H-H, Z-Z).
- Interference sequence (H-Z-H = `|1>`).
- Entanglement creation, partner lookup, breaking, and merging with a third qubit.
- Measurement statistics over 200 trials (verifying roughly 50/50 distribution).
- Splitter routing by state and direction.
- Sink counting for superposition targets.
- Two-cell two-qubit gate export to Qiskit.
- Three-cell Toffoli export to Qiskit.
- Removed gates and algorithm-as-level constraints.
- Error handling (`_safe_transform` catches exceptions without crashing).
- Measurement histogram capping at 20 entries.

Tests import directly from the package (`from src.core.entities import ...`) and run with `python -m pytest tests/ -v`.
