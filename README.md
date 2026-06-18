# Superposed

A 2D quantum computing puzzle game built with pygame, inspired by factory builders like Shapez. Place quantum gates on a conveyor grid to manipulate qubits and solve puzzles that teach real quantum mechanics concepts.

## Quantum Concepts

Superposed models five core ideas from quantum computing, mapped to a visual factory metaphor:

- **Basis states** — qubits flow as coloured particles: red for `|0>`, blue for `|1>`.
- **Superposition** — the Hadamard gate puts a qubit into superposition (purple), meaning it is both `|0>` and `|1>` until observed.
- **Phase** — qubits show their phase with an arrow; Z flips that phase and H can turn the difference into a visible state change.
- **Interference** — H then Z then H produces a deterministic `|1>`, demonstrating constructive/destructive interference via phase angle.
- **Entanglement** — the CNOT gate entangles two qubits into a Bell pair. Measuring one instantly collapses the other to the same state.

## Getting Started

### Requirements

- Python 3.9+
- pygame 2.1+

### Install and Run

```bash
# Clone the repo
git clone <repo-url>
cd Superposed

# Install dependencies
pip install pygame

# Run the game
python run.py

# Or as a package
python -m src
```

### Install as a Package

```bash
pip install -e .
superposed
```

## How to Play

The game has two modes accessible from the main menu:

**Campaign** — a chapter-based progression. The campaign introduces one concept at a time, from basic belt transport through entanglement, noise, error detection, Deutsch's algorithm, and algorithm-building challenges. Each level locks certain tiles and restricts which gates you can use, with a target number of qubits to deliver to the output sink.

**Sandbox** — an open canvas with every gate unlocked and no win condition, for free experimentation.

### Controls

| Key / Action | Effect |
|---|---|
| WASD / Arrows | Pan camera |
| Scroll wheel | Zoom in/out |
| 1-9 | Select gate from toolbar |
| Left click | Place selected gate |
| Left-click + drag (belt) | Lay a continuous line of belts |
| Right click / drag | Remove gates |
| R | Rotate selected gate |
| Space | Pause simulation |
| C | Clear all non-locked tiles |
| F | Show level briefing |
| X | Recenter camera |
| Tab | Return to menu |
| Middle-click sink | Cycle sink target state |

## Gate Reference

| Gate | Category | What it does |
|---|---|---|
| **Belt** | Infrastructure | Moves qubits in the arrow direction |
| **Generator** | Infrastructure | Spawns `\|0>` qubits at a fixed rate |
| **Output Sink** | Infrastructure | Collects qubits; tracks how many match the target state |
| **Hadamard (H)** | Single-qubit | `\|0>` or `\|1>` becomes superposition; superposition collapses back based on phase |
| **X (NOT)** | Single-qubit | Flips `\|0>` to `\|1>` and vice versa; superposition unchanged |
| **Y (Pauli-Y)** | Single-qubit | Flips `\|0>` and `\|1>`, and toggles phase on superposition |
| **Z (Phase)** | Single-qubit | Flips qubit phase; the phase arrow makes this visible before interference |
| **CNOT** | Two-qubit | Two-cell gate: control dot lane plus target gate lane. If control is `\|1>`, flips target. If superposed, entangles both |
| **CZ** | Two-qubit | Controlled phase flip; useful for phase kickback and interference |
| **SWAP** | Two-qubit | Exchanges the states of two qubits |
| **Toffoli** | Three-qubit | Controlled-controlled NOT: flips the target only when both controls are `\|1>` |
| **Measurement** | Consumer | Collapses superposition to `\|0>` or `\|1>` (50/50). Shows a histogram of results |
| **Splitter** | Router | Measures then routes: `\|0>` goes straight, `\|1>` turns clockwise |

## Project Structure

```
Superposed/
├── build-executable.md     # Standalone build notes
├── pyproject.toml          # Package metadata, entry point
├── run.py                  # Quick launcher
├── src/                    # Main package
│   ├── __init__.py         # __version__ = "1.0"
│   ├── __main__.py         # python -m src
│   ├── main.py             # Game loop and state machine
│   ├── core/               # Data model
│   │   ├── config.py       # Constants, colours, sizes
│   │   ├── entities.py     # QubitItem, Tile, Direction, QubitState
│   │   └── world.py        # WorldState, entanglement registry, camera
│   ├── engine/             # Simulation and gates
│   │   ├── gate_registry.py    # GateDef, register(), auto-loader
│   │   ├── simulation.py       # Physics loop, gate dispatch
│   │   └── gates/              # Registered gate modules
│   ├── ui/                 # Rendering and input
│   │   ├── rendering.py    # Grid, toolbar, HUD, qubit drawing
│   │   ├── sprites.py      # Sprite generation and caching
│   │   ├── menu.py         # Main menu, campaign select, briefing overlay, win screen
│   │   └── input_handler.py    # Keyboard, mouse, zoom
│   └── content/            # Game content
│       └── levels.py       # Campaign level definitions
├── assets/gates_sprites/   # Custom gate PNGs
├── tests/
│   └── test_gates.py       # Unit tests
├── tools/
│   └── sprite_editor.html  # Visual sprite editor
└── docs/
    ├── ARCHITECTURE.md
    └── superposed_architecture.svg
```

For a deeper dive into the design, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Adding a New Gate

The gate registry pattern means adding a gate requires only one new file. Create a `.py` file in `src/engine/gates/` that calls `register()`:

```python
from ..gate_registry import register, GateDef, Category

def _transform(item):
    # Your gate logic here
    pass

register(GateDef(
    id="my_gate",
    name="My Gate",
    tip="Does something quantum",
    color=(100, 200, 150),
    category=Category.SINGLE,
    transform=_transform,
    order=25,
))
```

The gate will automatically appear in the toolbar, be handled by the simulation, and be available in level definitions — no other files need to change.

## Running Tests

```bash
python -m pytest tests/ -v
```

The test suite covers gate transforms, entanglement mechanics, measurement statistics, splitter routing, interference, sink counting, circuit export, and error handling.

## License

This project is not currently licensed for distribution.
