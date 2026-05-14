"""Tutorial level definitions for Superposed.

Each level is a dict with:
    name          – display title
    description   – short goal description shown in level select
    briefing      – longer text shown at level start
    hint          – in-game hint line
    pre_placed    – dict of (x,y) -> (BuildingType, Direction, [sink_target])
    locked        – set of (x,y) coords the player cannot modify
    available     – list of BuildingTypes the player can place
    win_count     – number of correct qubits at ANY goal sink to win
    camera        – (cx, cy) initial camera center in world coords
"""

from entities import BuildingType as B, Direction as D, QubitState as Q

# ── Shorthand ────────────────────────────────────────────────────────────────
UP, RIGHT, DOWN, LEFT = D.UP, D.RIGHT, D.DOWN, D.LEFT
ZERO, ONE, SUP = Q.ZERO, Q.ONE, Q.SUPERPOSITION


# ═══════════════════════════════════════════════════════════════════════════════
# Level 1 — Transport
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_1 = {
    "name": "Transport",
    "description": "Route qubits from generator to output.",
    "briefing": (
        "Welcome to Superposed!\n\n"
        "Your factory makes qubits — tiny quantum particles.\n"
        "The green machine spawns |0⟩ qubits (red dots).\n\n"
        "Goal: connect the generator to the output sink\n"
        "using conveyor belts.\n\n"
        "Left-click to place.  R to rotate.  Right-click to remove."
    ),
    "hint": "Place belts to connect the generator to the sink →",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (6, 2):  (B.OUTPUT_SINK, RIGHT, ZERO),
    },
    "locked": {(0, 2), (6, 2)},
    "available": [B.BELT],
    "win_count": 5,
    "camera": (3, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 2 — Quantum NOT (X Gate)
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_2 = {
    "name": "Quantum NOT",
    "description": "Flip |0⟩ into |1⟩ using the X gate.",
    "briefing": (
        "The X gate is the quantum NOT gate.\n"
        "It flips |0⟩ (red) into |1⟩ (blue) and vice versa.\n\n"
        "The sink wants blue |1⟩ qubits, but the generator\n"
        "only makes red |0⟩.  Use the X gate to flip them!"
    ),
    "hint": "Place an X gate on the path to flip |0⟩ → |1⟩",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (7, 2):  (B.OUTPUT_SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [B.BELT, B.X_GATE],
    "win_count": 5,
    "camera": (3, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 3 — Superposition (Hadamard)
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_3 = {
    "name": "Superposition",
    "description": "Create a qubit that is both 0 and 1 at once.",
    "briefing": (
        "The Hadamard gate (H) puts a qubit into\n"
        "superposition — it becomes both |0⟩ AND |1⟩\n"
        "at the same time!  It turns purple.\n\n"
        "Route qubits through H to make them purple,\n"
        "then deliver them to the sink."
    ),
    "hint": "H gate turns red |0⟩ qubits purple (superposition)",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (7, 2):  (B.OUTPUT_SINK, RIGHT, SUP),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [B.BELT, B.HADAMARD],
    "win_count": 5,
    "camera": (3, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 4 — Collapse (Measurement)
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_4 = {
    "name": "Collapse",
    "description": "Observe what happens when you measure superposition.",
    "briefing": (
        "Measurement collapses superposition!\n\n"
        "A purple (superposed) qubit becomes either red |0⟩\n"
        "or blue |1⟩ with equal probability — 50/50.\n"
        "You can never predict which.\n\n"
        "Route qubits through H then Measurement.\n"
        "Watch the histogram — it should be roughly even.\n"
        "Deliver 10 qubits to the sink (any state counts)."
    ),
    "hint": "H → Measure gives a random 50/50 outcome each time",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (9, 2):  (B.OUTPUT_SINK, RIGHT, None),   # accepts anything
    },
    "locked": {(0, 2), (9, 2)},
    "available": [B.BELT, B.HADAMARD, B.MEASUREMENT],
    "win_count": 10,
    "camera": (4, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 5 — Interference (H → Z → H)
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_5 = {
    "name": "Interference",
    "description": "Discover how H → Z → H always produces |1⟩.",
    "briefing": (
        "The Z gate flips the phase of a qubit.\n"
        "You can't see phase directly, but it matters!\n\n"
        "Try this: route qubits through  H → Z → H.\n"
        "Something remarkable happens — the output is\n"
        "always |1⟩, never random.  This is interference.\n\n"
        "The sink wants blue |1⟩ qubits.  Build the circuit!"
    ),
    "hint": "H → Z → H = guaranteed |1⟩  (interference!)",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (9, 2):  (B.OUTPUT_SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (9, 2)},
    "available": [B.BELT, B.HADAMARD, B.Z_GATE],
    "win_count": 5,
    "camera": (4, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 6 — Entanglement (CNOT)
# ═══════════════════════════════════════════════════════════════════════════════
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
        # Control path: generator at top, feeds DOWN into CNOT
        (4, -1): (B.GENERATOR,   DOWN,  None),
        # Target path: generator at left, feeds RIGHT into CNOT
        (-1, 2): (B.GENERATOR,   RIGHT, None),
        # CNOT gate in the middle
        (4, 2):  (B.CNOT,        RIGHT, None),
        # Output sinks
        (8, 2):  (B.OUTPUT_SINK, RIGHT, None),   # target output (RIGHT)
        (4, 6):  (B.OUTPUT_SINK, DOWN,  None),   # control output (DOWN)
    },
    "locked": {(4, -1), (-1, 2), (4, 2), (8, 2), (4, 6)},
    "available": [B.BELT, B.HADAMARD],
    "win_count": 5,
    "camera": (4, 2),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Level 7 — Quantum Router (Splitter)
# ═══════════════════════════════════════════════════════════════════════════════
LEVEL_7 = {
    "name": "Quantum Router",
    "description": "Route qubits by state: |0⟩ and |1⟩ go different ways.",
    "briefing": (
        "The Splitter measures a qubit and routes it:\n"
        "  |0⟩ (red) goes straight ahead\n"
        "  |1⟩ (blue) goes to the side\n\n"
        "Superposition qubits collapse when they hit\n"
        "the splitter — just like measurement.\n\n"
        "Route H → Splitter to split the stream 50/50\n"
        "into the two sinks."
    ),
    "hint": "H creates superposition → Splitter sorts them by state",
    "pre_placed": {
        (0, 2):  (B.GENERATOR,   RIGHT, None),
        (9, 2):  (B.OUTPUT_SINK, RIGHT, ZERO),   # |0⟩ goes straight
        (5, 6):  (B.OUTPUT_SINK, DOWN,  ONE),    # |1⟩ goes down (CW of RIGHT)
    },
    "locked": {(0, 2), (9, 2), (5, 6)},
    "available": [B.BELT, B.HADAMARD, B.SPLITTER],
    "win_count": 3,   # 3 correct at either sink
    "camera": (4, 3),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Ordered list of all levels
# ═══════════════════════════════════════════════════════════════════════════════
ALL_LEVELS = [
    LEVEL_1,
    LEVEL_2,
    LEVEL_3,
    LEVEL_4,
    LEVEL_5,
    LEVEL_6,
    LEVEL_7,
]
