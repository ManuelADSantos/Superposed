"""Tutorial level definitions for Superposed.

Buildings are referenced by string gate IDs (see gate_registry).
"""

from __future__ import annotations

from ..core.entities import Direction as D, QubitState as Q

UP, RIGHT, DOWN, LEFT = D.UP, D.RIGHT, D.DOWN, D.LEFT
ZERO, ONE, SUP = Q.ZERO, Q.ONE, Q.SUPERPOSITION

# Gate IDs (strings)
BELT = "belt"
GEN = "generator"
SINK = "output_sink"
H = "hadamard"
X = "x_gate"
Z = "z_gate"
CNOT = "cnot"
MEAS = "measurement"
SPLIT = "splitter"


LEVEL_1 = {
    "name": "Transport",
    "description": "Route qubits from generator to output.",
    "briefing": (
        "Welcome to Superposed!\n\n"
        "Your factory makes qubits — tiny quantum particles.\n"
        "The green machine spawns |0> qubits (red dots).\n\n"
        "Goal: connect the generator to the output sink\n"
        "using conveyor belts.\n\n"
        "Left-click to place.  R to rotate.  Right-click to remove."
    ),
    "hint": "Place belts to connect the generator to the sink →",
    "pre_placed": {
        (0, 2):  (GEN,  RIGHT, None),
        (6, 2):  (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 2), (6, 2)},
    "available": [BELT],
    "win_count": 5,
    "camera": (3, 2),
}

LEVEL_2 = {
    "name": "Quantum NOT",
    "description": "Flip |0> into |1> using the X gate.",
    "briefing": (
        "The X gate is the quantum NOT gate.\n"
        "It flips |0> (red) into |1> (blue) and vice versa.\n\n"
        "The sink wants blue |1> qubits, but the generator\n"
        "only makes red |0>.  Use the X gate to flip them!"
    ),
    "hint": "Place an X gate on the path to flip |0> → |1>",
    "pre_placed": {
        (0, 2):  (GEN,  RIGHT, None),
        (7, 2):  (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (3, 2),
}

LEVEL_3 = {
    "name": "Superposition",
    "description": "Create a qubit that is both 0 and 1 at once.",
    "briefing": (
        "The Hadamard gate (H) puts a qubit into\n"
        "superposition — it becomes both |0> AND |1>\n"
        "at the same time!  It turns purple.\n\n"
        "Route qubits through H to make them purple,\n"
        "then deliver them to the sink."
    ),
    "hint": "H gate turns red |0> qubits purple (superposition)",
    "pre_placed": {
        (0, 2):  (GEN,  RIGHT, None),
        (7, 2):  (SINK, RIGHT, SUP),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (3, 2),
}

LEVEL_4 = {
    "name": "Collapse",
    "description": "Observe what happens when you measure superposition.",
    "briefing": (
        "Measurement collapses superposition!\n\n"
        "A purple (superposed) qubit becomes either red |0>\n"
        "or blue |1> with equal probability — 50/50.\n"
        "You can never predict which.\n\n"
        "Route qubits through H then Measurement.\n"
        "Watch the histogram — it should be roughly even.\n"
        "Deliver 10 qubits to the sink (any state counts)."
    ),
    "hint": "H → Measure gives a random 50/50 outcome each time",
    "pre_placed": {
        (0, 2):  (GEN,  RIGHT, None),
        (9, 2):  (SINK, RIGHT, None),
    },
    "locked": {(0, 2), (9, 2)},
    "available": [BELT, H, MEAS],
    "win_count": 10,
    "camera": (4, 2),
}

LEVEL_5 = {
    "name": "Interference",
    "description": "Discover how H -> Z -> H always produces |1>.",
    "briefing": (
        "The Z gate flips the phase of a qubit.\n"
        "You can't see phase directly, but it matters!\n\n"
        "Try this: route qubits through  H → Z → H.\n"
        "Something remarkable happens — the output is\n"
        "always |1>, never random.  This is interference.\n\n"
        "The sink wants blue |1> qubits.  Build the circuit!"
    ),
    "hint": "H -> Z -> H = guaranteed |1>  (interference!)",
    "pre_placed": {
        (0, 2):  (GEN,  RIGHT, None),
        (9, 2):  (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (9, 2)},
    "available": [BELT, H, Z],
    "win_count": 5,
    "camera": (4, 2),
}

LEVEL_6 = {
    "name": "Entanglement",
    "description": "Link two qubits so measuring one affects the other.",
    "briefing": (
        "The CNOT gate links two qubits together.\n"
        "It takes a CONTROL qubit (from the side)\n"
        "and a TARGET qubit (from behind).\n\n"
        "If the control is in superposition,\n"
        "both qubits become entangled — measuring one\n"
        "instantly determines the other!\n\n"
        "Put H on the control path to create\n"
        "superposition, then feed both into the CNOT."
    ),
    "hint": "Put H on the control (top) path before the CNOT",
    "pre_placed": {
        (4, -1): (GEN,   DOWN,  None),
        (-1, 2): (GEN,   RIGHT, None),
        (4, 2):  (CNOT,  RIGHT, None),
        (8, 2):  (SINK,  RIGHT, None),
        (4, 6):  (SINK,  DOWN,  None),
    },
    "locked": {(4, -1), (-1, 2), (4, 2), (8, 2), (4, 6)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (4, 2),
}

LEVEL_7 = {
    "name": "Quantum Router",
    "description": "Route qubits by state: |0> and |1> go different ways.",
    "briefing": (
        "The Splitter measures a qubit and routes it:\n"
        "  |0> (red) goes straight ahead\n"
        "  |1> (blue) goes to the side\n\n"
        "Superposition qubits collapse when they hit\n"
        "the splitter — just like measurement.\n\n"
        "Route H → Splitter to split the stream 50/50\n"
        "into the two sinks."
    ),
    "hint": "H creates superposition → Splitter sorts them by state",
    "pre_placed": {
        (0, 2):  (GEN,   RIGHT, None),
        (9, 2):  (SINK,  RIGHT, ZERO),
        (5, 6):  (SINK,  DOWN,  ONE),
    },
    "locked": {(0, 2), (9, 2), (5, 6)},
    "available": [BELT, H, SPLIT],
    "win_count": 3,
    "camera": (4, 3),
}


ALL_LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6, LEVEL_7]
