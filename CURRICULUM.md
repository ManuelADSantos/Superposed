# Superposed - Curriculum

11 chapters, 26 levels, 14 gate types.

## Chapter 1: Classical Foundations (3 levels)

Concept: information is carried by signals; qubits travel on conveyor belts.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 1 | Transport | Belt routing: connect generator to sink | Belt | Build corridor |
| 2 | Quantum NOT | X gate flips \|0> to \|1> (classical NOT) | Belt, X | X:1, corridor |
| 3 | Parallel Tracks | Multiple independent lanes | Belt, X | X:1, lanes only |

Learning outcome: the player understands the factory metaphor (generators produce qubits, belts carry them, sinks consume them) and can flip a qubit with X.

## Chapter 2: Superposition (3 levels)

Concept: the Hadamard gate puts a qubit into both \|0> and \|1> simultaneously.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 4 | Superposition | H creates \|+> from \|0> | Belt, H | H:1, corridor |
| 5 | Three Lanes | Multiple superposed outputs | Belt, X, H | X:1, H:1, lanes only |
| 6 | Fixed Pieces | Working around locked (pre-placed) gates | Belt, H | H:1, locked gates, lanes only |

Learning outcome: superposition is a real third state, not just "random"; H is its own inverse.

## Chapter 3: Measurement (2 levels)

Concept: measuring a superposed qubit collapses it to \|0> or \|1> probabilistically.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 7 | Collapse | Measurement gate collapses superposition | Belt, H, Meas | Build corridor (2 cells) |
| 8 | Quantum Router | Splitter routes \|0> up and \|1> down | Belt, H, Split | H:1, Split:1 |

Learning outcome: measurement is irreversible and probabilistic; the splitter separates measurement outcomes spatially.

## Chapter 4: Phase & Interference (3 levels)

Concept: Z flips the phase of \|1> without changing measurement probabilities; H converts phase differences into amplitude differences (interference).

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 9 | Interference | H-Z-H produces deterministic \|1> via interference | Belt, H, Z | H:2, Z:1, corridor |
| 10 | Pauli Y | Y gate = i*X*Z (combined bit+phase flip) | Belt, Y | Y:1, locked H, corridor |
| 11 | Y Sandwiched | H-Y-H and composing rotations | Belt, Y | Y:1, locked H pair, build corridor only |

Learning outcome: phase is invisible to measurement but real; interference converts hidden phase into observable outcomes.

## Chapter 5: Entanglement (2 levels)

Concept: CNOT creates correlations between qubits that persist across distance.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 12 | Controlled Flip | CNOT flips target when control is \|1> | Belt, X | X:1, locked CNOT + target path, build top row only |
| 13 | Bell State | Entangled pair: H then CNOT creates correlated measurements | Belt, H, CNOT, Meas | H:1, CNOT:1, Meas:2, lane band; win by measuring 10 |

Learning outcome: CNOT is a conditional gate; entanglement creates perfect correlations that can't be explained classically. Entangled qubits display a gold ring and show \|?> on hover, reflecting the maximally mixed reduced state.

## Chapter 6: Multi-Qubit Ops (2 levels)

Concept: CZ applies phase kickback; SWAP exchanges two qubit states.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 14 | Phase Kickback | CZ + H produces deterministic \|1> via phase kickback | Belt, H, X, CZ | H:2, X:1, CZ:1, lane band |
| 15 | State Exchange | SWAP exchanges qubit states between lanes | Belt, SWAP | SWAP:1, build area whitelist, locked X |

Learning outcome: CZ is symmetric (both qubits "feel" the interaction); SWAP is a routing primitive.

## Chapter 7: Quantum Circuits (1 level)

Concept: entanglement doesn't stop at two qubits — chaining CNOT gates propagates correlations across many qubit streams.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 16 | Entanglement Chain | Entanglement propagates through CNOT chains | Belt, H, CNOT | H:1, CNOT:2, lane band, sinks want \|1> |

Learning outcome: entanglement scales through chaining; creative circuit design is needed when resources (gates) are limited.

## Chapter 8: Quantum Noise (3 levels)

Concept: the noise gate randomizes a qubit's state and exit direction, modelling real-world decoherence. It is never player-placed — always a locked obstacle to route around.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 17 | Noisy Channel | Noise gate scrambles qubits; route around it | Belt | - |
| 18 | Noise Breaks Everything | Noise destroys interference (H-Z-Noise-H is random) | Belt, H, Z | H:4, Z:2 |
| 19 | Detour & Transform | Route around noise AND apply the right gates (X for \|1>, H for \|+>) | Belt, X, H | X:1, H:1 |

Learning outcome: noise is the fundamental enemy of quantum computation; careful routing avoids corruption; real quantum computing combines noise avoidance with gate transformations.

## Chapter 9: Noise Management (2 levels)

Concept: sometimes you can't avoid noise entirely — use splitters and filters to recover useful qubits from noisy streams.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 20 | Scatter Catch | Noise scatters qubits in all directions; place sinks to catch them | Belt, Sink | Sink:3 |
| 21 | Noisy Filter | Sort scattered noise output with splitters | Belt, Split | Split:3 |

Learning outcome: noise management is about probabilistic recovery, not perfect prevention.

## Chapter 10: Quantum Cloning (1 level)

Concept: CNOT copies known basis states but cannot clone unknown quantum states (no-cloning theorem).

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 22 | Backup Before Noise | CNOT duplicates a classical \|1> before noise can destroy it | Belt, X, CNOT | CNOT:1 |

Learning outcome: classical information can be copied; quantum information cannot. This asymmetry is fundamental.

## Chapter 11: Algorithms (4 levels)

Concept: famous quantum algorithms are built from the same small gates the player already knows.

| # | Level | Teaches | Gates | Constraint |
|---|-------|---------|-------|------------|
| 23 | Deutsch Classifier | Build constant (H-H) and balanced (H-Z-H) paths; route with splitters | Belt, H, Z | H:4, Z:1, lanes only |
| 24 | QFT Shape | Two-lane QFT structure with H, CZ, SWAP | Belt | H:2, CZ:1, SWAP:1 (all pre-placed), lane band |
| 25 | Grover Search | Full 2-qubit Grover: H, CZ oracle, H-X-CZ-X-H diffusion | Belt, H, X, CZ | H:6, X:4, CZ:2, lane band |
| 26 | Teleport Blueprint | Bell pair + Bell measurement half of quantum teleportation | Belt, H, CNOT | H:2, CNOT:2, lane band |

Learning outcome: algorithms are not magic — they are specific arrangements of gates the player already knows. The player has built toy versions of four landmark algorithms.

## Gate Introduction Order

| Gate | First appears | Chapter |
|------|---------------|---------|
| Belt | Level 1 | Classical Foundations |
| X | Level 2 | Classical Foundations |
| H (Hadamard) | Level 4 | Superposition |
| Measurement | Level 7 | Measurement |
| Splitter | Level 8 | Measurement |
| Z | Level 9 | Phase & Interference |
| Y | Level 10 | Phase & Interference |
| CNOT | Level 12 | Entanglement |
| CZ | Level 14 | Multi-Qubit Ops |
| SWAP | Level 15 | Multi-Qubit Ops |
| Noise | Level 17 | Quantum Noise |

## Pedagogical Principles

1. One concept per chapter. Each chapter introduces exactly one quantum idea and gives 1-3 levels to practice it before moving on.

2. Gate limits enforce intent. When a level has `gate_limits`, the player cannot brute-force a solution — they must use exactly the intended circuit structure. Nearly every level with gates ships an exact-fit budget.

3. Build-area whitelists (`unlocked`) restrict placement to highlighted cells, preventing detour exploits (e.g. bypassing locked H gates in Y Sandwiched) and keeping solutions on the intended circuit path. 19 of 26 levels use one; the exceptions (levels 8, 17-22) are the free-routing puzzles where finding a path through 2D space IS the challenge.

4. Locked pieces scaffold learning. Pre-placed gates show the player what the circuit should look like; they only need to fill in the missing parts.

5. Compact layouts reduce busywork. Every level is designed so that the puzzle content (the interesting part) is close together, minimizing time spent placing filler belts.

6. Win conditions match the concept. Sink-based levels test deterministic outputs; measure-based levels test probabilistic understanding (entanglement, teleportation).

7. Difficulty ramp: chapters 1-6 introduce individual concepts, 7 combines entanglement at scale, 8-9 add noise as an obstacle, 10 addresses cloning limits, and 11 is the capstone (algorithms).

8. Entangled qubits show a gold ring and display \|?> on hover, with their Bloch sphere vector at the origin — physically correct for the maximally mixed reduced state.
