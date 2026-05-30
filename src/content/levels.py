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


LEVEL_8 = {
    "name": "Parallel Tracks",
    "description": "Two generators, two sinks — each lane needs different treatment.",
    "briefing": (
        "Two assembly lines, two targets.\n\n"
        "Top sink wants |0> — the generator already makes that,\n"
        "so just run a belt straight across.\n\n"
        "Bottom sink wants |1> — you'll need to flip the qubit\n"
        "with an X gate somewhere along the path.\n\n"
        "Build both pipelines at the same time!"
    ),
    "hint": "Top: belt only → |0>.  Bottom: add X gate → |1>",
    "pre_placed": {
        (0, 0):  (GEN,  RIGHT, None),
        (9, 0):  (SINK, RIGHT, ZERO),
        (0, 5):  (GEN,  RIGHT, None),
        (9, 5):  (SINK, RIGHT, ONE),
    },
    "locked": {(0, 0), (9, 0), (0, 5), (9, 5)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (4, 2),
}

LEVEL_9 = {
    "name": "Quantum Fork",
    "description": "Split a superposition stream and sort qubits to matching sinks.",
    "briefing": (
        "The Splitter measures and routes:\n"
        "  |0> (red)  → exits straight ahead\n"
        "  |1> (blue) → exits clockwise (to the right when facing right = downward)\n\n"
        "First use H to create superposition, then Splitter\n"
        "divides the stream 50/50 by state.\n\n"
        "Route each outcome to its matching sink.\n"
        "Win when either sink collects 3."
    ),
    "hint": "H → Splitter → |0> forward to ZERO sink, |1> down to ONE sink",
    "pre_placed": {
        (0, 3):   (GEN,  RIGHT, None),
        (10, 3):  (SINK, RIGHT, ZERO),
        (6, 9):   (SINK, DOWN,  ONE),
    },
    "locked": {(0, 3), (10, 3), (6, 9)},
    "available": [BELT, H, SPLIT],
    "win_count": 3,
    "camera": (5, 5),
}

LEVEL_10 = {
    "name": "Bell Factory",
    "description": "Place the CNOT yourself to build your own entangled pairs.",
    "briefing": (
        "In Level 6 the CNOT was given to you.\n"
        "Now you place it.\n\n"
        "CNOT needs two input streams:\n"
        "  Target  — enters from behind (the gate's back)\n"
        "  Control — enters from the side\n\n"
        "The two generators meet at a natural crossing point.\n"
        "Place CNOT there (facing right), add H on the control\n"
        "path to create superposition, then wire both outputs\n"
        "to their sinks."
    ),
    "hint": "CNOT goes at the stream crossing — H on the vertical (control) path",
    "pre_placed": {
        (-1, 3):  (GEN,  RIGHT, None),
        (5,  -1): (GEN,  DOWN,  None),
        (10, 3):  (SINK, RIGHT, None),
        (5,  8):  (SINK, DOWN,  None),
    },
    "locked": {(-1, 3), (5, -1), (10, 3), (5, 8)},
    "available": [BELT, H, CNOT],
    "win_count": 5,
    "camera": (5, 3),
}

LEVEL_11 = {
    "name": "Three Lanes",
    "description": "Route three streams — each needs a different quantum transformation.",
    "briefing": (
        "Three generators, three sinks, three target states.\n\n"
        "  Top lane:    deliver |0> unchanged\n"
        "  Middle lane: flip |0> into |1>\n"
        "  Bottom lane: put |0> into superposition\n\n"
        "Each lane is independent — build them in any order.\n"
        "You already know every gate needed!"
    ),
    "hint": "Top: belt. Middle: X gate. Bottom: H gate.",
    "pre_placed": {
        (0, 0):  (GEN,  RIGHT, None),
        (9, 0):  (SINK, RIGHT, ZERO),
        (0, 4):  (GEN,  RIGHT, None),
        (9, 4):  (SINK, RIGHT, ONE),
        (0, 8):  (GEN,  RIGHT, None),
        (9, 8):  (SINK, RIGHT, SUP),
    },
    "locked": {(0, 0), (9, 0), (0, 4), (9, 4), (0, 8), (9, 8)},
    "available": [BELT, X, H],
    "win_count": 5,
    "camera": (4, 4),
}

LEVEL_12 = {
    "name": "Fixed Pieces",
    "description": "Locked gates are part of the circuit — use them, don't fight them.",
    "briefing": (
        "Some tiles are locked and can't be moved or removed.\n"
        "But qubits still pass through them!\n\n"
        "Top path: a locked X gate is already installed.\n"
        "  Connect it with belts — it flips |0> to |1> for you.\n\n"
        "Bottom path: needs superposition.\n"
        "  No locked gates here — place H yourself.\n\n"
        "Read the board before you build."
    ),
    "hint": "Top: belt around the locked X. Bottom: place an H gate.",
    "pre_placed": {
        (0, 0):  (GEN,  RIGHT, None),
        (4, 0):  (X,    RIGHT, None),
        (9, 0):  (SINK, RIGHT, ONE),
        (0, 5):  (GEN,  RIGHT, None),
        (9, 5):  (SINK, RIGHT, SUP),
    },
    "locked": {(0, 0), (4, 0), (9, 0), (0, 5), (9, 5)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (4, 2),
}

LEVEL_13 = {
    "name": "Quantum Crossroads",
    "description": "One stream, two destinations — split by state to fill both sinks.",
    "briefing": (
        "You have one generator and two hungry sinks:\n"
        "  Right sink wants superposition |±>\n"
        "  Bottom sink wants |1>\n\n"
        "Strategy:\n"
        "  H → Splitter divides the stream.\n"
        "  |0> exits forward — apply H again to make superposition.\n"
        "  |1> exits downward — belt it straight to the ONE sink.\n\n"
        "Win when either sink collects 3."
    ),
    "hint": "H → Split → (|0> forward: H → SUP sink), (|1> down: ONE sink)",
    "pre_placed": {
        (0, 3):  (GEN,  RIGHT, None),
        (10, 3): (SINK, RIGHT, SUP),
        (5, 9):  (SINK, DOWN,  ONE),
    },
    "locked": {(0, 3), (10, 3), (5, 9)},
    "available": [BELT, H, SPLIT],
    "win_count": 3,
    "camera": (5, 5),
}


ALL_LEVELS = [
    LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6, LEVEL_7,
    LEVEL_8, LEVEL_9, LEVEL_10, LEVEL_11, LEVEL_12, LEVEL_13,
]
