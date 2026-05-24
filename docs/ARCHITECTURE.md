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

## Entry Points

There are three ways to start the game, and all of them call the same `main()` function in `src/main.py`:

1. `python run.py` — direct script execution, imports `src.main`.
2. `python -m src` — package execution via `__main__.py`, uses a relative import.
3. `superposed` — CLI command after `pip install -e .`, configured in `pyproject.toml`.

## Game Loop and State Machine

`main.py` runs the game loop with a state machine driven by the `GameState` enum (defined in `ui/menu.py`). The states are:

```
MAIN_MENU → LEVEL_SELECT → BRIEFING → LEVEL_PLAY → WIN_SCREEN
                                                  ↓
MAIN_MENU → SANDBOX ←──────────────────── (Tab key)
```

Each frame follows the same sequence: process input, update simulation (if not paused), render everything. The state determines which input handler and renderer are active — for example, `MAIN_MENU` only draws the menu and listens for button clicks, while `LEVEL_PLAY` runs the full simulation loop.

## Core Subpackage

### config.py

Flat module of constants: window size, tile size, physics speeds, UI dimensions, and the colour palette. `WIDTH` and `HEIGHT` are mutable — `main.py` overwrites them after creating the pygame window to support different screen sizes.

### entities.py

Defines the fundamental data types:

**Direction** — enum with UP, RIGHT, DOWN, LEFT and helper functions for rotation (`cw_dir`, `ccw_dir`, `opposite_dir`) and delta conversion.

**QubitState** — enum with ZERO, ONE, SUPERPOSITION. The `state_color()` function maps these to red, blue, and purple respectively.

**QubitItem** — a qubit particle flowing through the factory. Tracks its quantum state, phase flag, entanglement group, progress along the current tile, and disappearance animation state. Each instance gets a unique `uid` from a counter.

**Tile** — a single grid cell. Holds the building ID (a string like `"hadamard"`), direction, the qubit currently on it, a second slot for the control qubit (used by CNOT), spawn/process timers, measurement histogram, and sink output counters.

### world.py

All mutable game state lives in the `WorldState` class: the sparse grid (a `dict` mapping `(x, y)` to `Tile`), camera position and zoom, entanglement tracking, and the current level definition.

The entanglement registry is a pair of structures — `entangle_groups` maps a group ID to a set of qubit UIDs, and `entangle_lookup` maps a qubit UID to its group ID. This allows O(1) partner lookups when measurement collapses one qubit.

For backward compatibility, module-level proxy variables (`world`, `camera_x`, `zoom`, etc.) are kept in sync via `_sync_from_state()` and `_sync_to_state()` helpers. Code that reads `world.camera_x` works the same as `WorldState.camera_x`.

**Key functions:**
- `reset_world()` — reinitialises all state, clears sprite caches.
- `load_level(level_def, index)` — places pre-built tiles, sets locked positions, configures camera.
- `check_win_condition()` — returns True when every sink has met its target count.

## Engine Subpackage

### gate_registry.py

The central registry is a dictionary mapping string IDs to `GateDef` dataclass instances. Each `GateDef` carries the gate's metadata (name, tooltip, colour), its `category` (which determines how the simulation calls it), its `transform` function, and optional sprite/overlay callbacks.

**Categories and their transform signatures:**

| Category | Signature | When called |
|---|---|---|
| INFRASTRUCTURE | — | Hardcoded in simulation (belt movement, spawning, collecting) |
| SINGLE | `transform(item)` | When a qubit arrives at the gate tile |
| TWO_QUBIT | `transform(control, target)` | When both control and target slots are occupied |
| CONSUMER | `transform(item, tile)` | Qubit is consumed (measurement records to tile) |
| ROUTER | `transform(x, y, tile, item, eject_fn)` | Gate controls where the qubit goes next |

**Auto-loader:** `load_gates()` scans the `gates/` directory, imports every `.py` file in sorted order, and each file calls `register()` at module scope. This means adding a new gate is a single-file operation with zero changes to existing code.

**Toolbar:** `active_toolbar(available)` filters the full registry to only the gates allowed in the current level, preserving the `order` field for consistent toolbar layout.

### simulation.py

`update_items(dt)` is the physics loop, called once per frame. It iterates every tile in the world and:

1. **Advances progress** — qubits on belts move forward by `BELT_SPEED * dt`. When progress reaches 1.0, the qubit is ready to transfer.
2. **Spawns qubits** — generator tiles create new `QubitItem(ZERO)` at a fixed rate.
3. **Processes two-qubit gates** — CNOT tiles wait for both control and target slots to fill (with a short delay for visual clarity), then call the gate's transform and eject both qubits.
4. **Applies single-qubit gates** — when a qubit arrives (progress crosses 0.0), the gate's transform is called immediately.
5. **Transfers qubits** — when a qubit finishes a tile, it moves to the next tile in the facing direction. If the next tile doesn't exist or is full, the qubit starts a disappearance animation.

`_safe_transform(gate, *args)` wraps every gate call in a try/except so a buggy gate definition can never crash the game — it prints to stderr and leaves the qubit unmodified.

**CNOT routing:** the control qubit arrives from the counter-clockwise perpendicular direction (e.g., if the CNOT faces RIGHT, control comes from above). The target arrives from behind (the opposite of the gate's direction). This is enforced by the simulation's arrival-direction check.

### gates/

Each gate file follows the same pattern: define a `_transform` function, optionally a `_sprite` function, then call `register()` with a `GateDef`. The files are:

- **_infrastructure.py** — Belt, Generator, Output Sink. These have no transform (simulation handles them directly) but provide sprite functions.
- **hadamard.py** — Creates superposition from basis states, collapses superposition based on phase. Breaks entanglement on collapse.
- **x_gate.py** — NOT gate, flips |0> and |1>. Superposition is unchanged.
- **z_gate.py** — Phase gate, toggles `phase_flipped` on superposed qubits only.
- **cnot.py** — Two-qubit gate. If control is |1>, flips target. If control is superposed, puts target into superposition and entangles both via the world's entanglement registry.
- **measurement.py** — Consumer gate. Collapses superposition to |0> or |1> with 50/50 probability. Collapses entangled partners to the same state. Records results in a tile-level histogram (capped at 20 entries). Includes an overlay function that draws the histogram directly on the tile.
- **splitter.py** — Router gate. Implicitly measures the qubit, then routes |0> straight ahead and |1> clockwise. Used to separate qubit states spatially.

## UI Subpackage

### rendering.py (292 lines)

The largest file in the project. Draws the grid, buildings, qubits, toolbar, HUD, level progress, and ghost previews. Key functions:

- `draw_grid()` — iterates visible tiles and blits cached building sprites with directional rotation. Draws qubit particles on top with glow effects.
- `draw_qubit_item()` — standalone function that renders a qubit with state colour, entanglement halo, and fade-out animation. Extracted to its own function to avoid circular imports.
- `draw_toolbar()` — renders the bottom toolbar with building buttons, pause indicator, and step counter.
- `draw_level_hud()` — shows level name, objective text, and a progress bar for sink completion.

### sprites.py

Sprite generation follows a three-tier resolution chain:

1. **Custom PNG** — looks for `assets/sprites/<gate_id>.png` and rotates it to match the gate's direction.
2. **Registry sprite_fn** — calls `gate.sprite_fn(direction, size)` if the gate definition provides one.
3. **Generic fallback** — draws a coloured rounded rectangle with the gate's initial.

All sprites are cached via `@lru_cache`. The caches are cleared on `reset_world()` to handle resolution changes.

The file also exports public drawing primitives (`_panel`, `_arrow`, `_shadow`, etc.) that gate sprite functions import to maintain visual consistency.

### menu.py (343 lines)

Implements four screens as draw/handle function pairs:

- **Main menu** — title, subtitle, two buttons (Levels, Sandbox), version number in the corner.
- **Level select** — 4-column grid of level cards with completion badges (stored in a module-level `completed_levels` set).
- **Briefing** — overlay before a level starts, showing the level name, description, and a START button.
- **Win screen** — overlay after completing a level, with MENU and NEXT LEVEL buttons.

### input_handler.py

Translates pygame events into game actions. Returns an updated `(selected_building, selected_rotation, paused, step_requested)` tuple each frame. Handles camera panning (WASD), zoom (scroll wheel), building placement (left click), removal (right click), rotation (R), and toolbar selection (number keys or clicking toolbar buttons).

## Content Subpackage

### levels.py

Seven tutorial levels, each defined as a dictionary with:

- `name`, `description`, `briefing` — text shown to the player.
- `pre_placed` — list of `(x, y, building_id, direction)` tuples for tiles the level starts with.
- `locked` — set of `(x, y)` coordinates the player cannot modify.
- `available` — list of gate IDs the player can use (restricts the toolbar).
- `win_count` — how many qubits the sink must collect to complete the level.
- `camera` — initial camera position.

The levels progress through the quantum concepts in order:

1. **Transport** — basic belt routing.
2. **Quantum NOT** — use X gate to flip |0> to |1>.
3. **Superposition** — use H gate to create purple |+> particles.
4. **Collapse** — measure superposition to see the 50/50 histogram.
5. **Interference** — H then Z then H produces deterministic |1>.
6. **Entanglement** — use CNOT to create correlated qubit pairs.
7. **Quantum Router** — use the Splitter to route by state.

## Design Decisions

### Sparse grid over 2D array

The world is a `dict[(int, int), Tile]` rather than a fixed-size 2D array. This means the sandbox mode has an effectively infinite canvas, tiles only consume memory when placed, and coordinate math stays simple (no bounds checking on the grid itself, only on the viewport).

### String IDs over enum for gates

Gates are identified by string keys (`"hadamard"`, `"belt"`) rather than an enum. This allows new gates to be added without modifying any central type definition — the registry is the only source of truth, and it's populated dynamically at import time.

### Phase flag over state vectors

Full quantum state vectors would be overkill for a puzzle game. Instead, superposition is a single enum value and phase is a boolean flag. This is enough to model H, X, Z, CNOT, measurement, and interference (H-Z-H) correctly, while keeping the simulation simple and the code approachable.

### Category-based dispatch

Rather than one giant if/elif chain in the simulation, gates declare their category and the simulation uses it to decide the calling convention. This keeps the simulation loop clean and makes the contract for each gate type explicit.

### Module-level world proxies

The `WorldState` class is the canonical state container, but module-level variables in `world.py` (like `world`, `camera_x`, `zoom`) provide convenient shorthand throughout the codebase. A pair of sync functions keeps them consistent. This avoids passing the state object through every function signature while still having a single place to reset everything.

## Test Coverage

The test suite (`tests/test_gates.py`, 37 tests) covers:

- Every gate transform (X, H, Z, CNOT, Measurement, Splitter) with basis states and superposition.
- Double-application identity checks (X-X, H-H, Z-Z).
- Interference sequence (H-Z-H = |1>).
- Entanglement creation, partner lookup, and breaking.
- Measurement statistics over 200 trials (verifying roughly 50/50 distribution).
- Splitter routing by state and direction.
- Error handling (`_safe_transform` catches exceptions without crashing).
- Measurement histogram capping at 20 entries.

Tests import directly from the package (`from src.core.entities import ...`) and run with `python -m pytest tests/ -v`.
