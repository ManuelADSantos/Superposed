"""Campaign content: chapters and levels.

Each chapter groups related levels, provides a concept explanation,
and specifies which gates are unlocked at that point in the progression.
ALL_LEVELS is derived by flattening all chapter level lists — global indices
remain stable for completion tracking.
"""

from __future__ import annotations

from ..core.entities import Direction as D, QubitState as Q

UP, RIGHT, DOWN, LEFT = D.UP, D.RIGHT, D.DOWN, D.LEFT
ZERO, ONE, SUP = Q.ZERO, Q.ONE, Q.SUPERPOSITION

BELT = "belt"
GEN = "generator"
SINK = "output_sink"
H = "hadamard"
X = "x_gate"
Y = "y_gate"
Z = "z_gate"
CNOT = "cnot"
CZ = "cz"
SWAP = "swap"
TOFFOLI = "toffoli"
MEAS = "measurement"
SPLIT = "splitter"
NOISE = "noise"
ORA_C = "oracle_constant"
ORA_B = "oracle_balanced"
DUP = "duplicator"


# ---------------------------------------------------------------------------
# Chapter 1: Classical Foundations
# ---------------------------------------------------------------------------

_CH1_CONCEPT = (
    "In computing, information is carried by signals — tiny pulses\n"
    "of energy traveling through circuits.\n\n"
    "In this factory, those signals are qubits. They travel\n"
    "along conveyor belts from generators to output sinks.\n\n"
    "Every qubit starts as |0> (red). The X gate is the quantum\n"
    "NOT gate — it flips |0> to |1> and |1> to |0>, just like\n"
    "a classical NOT."
)

CH1_L1 = {
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
    "hint": "Place belts to connect the generator to the sink ->",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (6, 2): (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 2), (6, 2)},
    "available": [BELT],
    "win_count": 5,
    "camera": (3, 2),
}

CH1_L2 = {
    "name": "Quantum NOT",
    "description": "Flip |0> into |1> using the X gate.",
    "briefing": (
        "The X gate is the quantum NOT gate.\n"
        "It flips |0> (red) into |1> (blue) and vice versa.\n\n"
        "The sink wants blue |1> qubits, but the generator\n"
        "only makes red |0>.  Use the X gate to flip them!"
    ),
    "hint": "Place an X gate on the path to flip |0> -> |1>",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (7, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (3, 2),
}

CH1_L3 = {
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
    "hint": "Top: belt only -> |0>.  Bottom: add X gate -> |1>",
    "pre_placed": {
        (0, 0): (GEN, RIGHT, None),
        (9, 0): (SINK, RIGHT, ZERO),
        (0, 5): (GEN, RIGHT, None),
        (9, 5): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 0), (9, 0), (0, 5), (9, 5)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (4, 2),
}


# ---------------------------------------------------------------------------
# Chapter 2: Superposition
# ---------------------------------------------------------------------------

_CH2_CONCEPT = (
    "Here's where quantum gets weird.\n\n"
    "Classical bits are EITHER 0 or 1. Qubits can be BOTH\n"
    "at the same time — this is called superposition.\n\n"
    "The Hadamard gate (H) creates superposition. It turns\n"
    "a definite state into a mix of both possibilities.\n"
    "A superposed qubit appears purple.\n\n"
    "When you measure a superposed qubit, it collapses to\n"
    "either |0> or |1> with equal probability — 50/50.\n"
    "The superposition is destroyed forever."
)

CH2_L1 = {
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
        (0, 2): (GEN, RIGHT, None),
        (7, 2): (SINK, RIGHT, SUP),
    },
    "locked": {(0, 2), (7, 2)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (3, 2),
}

CH2_L2 = {
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
        (0, 0): (GEN, RIGHT, None),
        (9, 0): (SINK, RIGHT, ZERO),
        (0, 4): (GEN, RIGHT, None),
        (9, 4): (SINK, RIGHT, ONE),
        (0, 8): (GEN, RIGHT, None),
        (9, 8): (SINK, RIGHT, SUP),
    },
    "locked": {(0, 0), (9, 0), (0, 4), (9, 4), (0, 8), (9, 8)},
    "available": [BELT, X, H],
    "win_count": 5,
    "camera": (4, 4),
}

CH2_L3 = {
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
        (0, 0): (GEN, RIGHT, None),
        (4, 0): (X, RIGHT, None),
        (9, 0): (SINK, RIGHT, ONE),
        (0, 5): (GEN, RIGHT, None),
        (9, 5): (SINK, RIGHT, SUP),
    },
    "locked": {(0, 0), (4, 0), (9, 0), (0, 5), (9, 5)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (4, 2),
}


# ---------------------------------------------------------------------------
# Chapter 3: Measurement & Routing
# ---------------------------------------------------------------------------

_CH3_CONCEPT = (
    "Measurement is how we extract information from qubits.\n\n"
    "When measured, a superposed qubit collapses — randomly\n"
    "becoming |0> or |1>. You can never predict which.\n"
    "This randomness is fundamental, not a limitation.\n\n"
    "The Splitter is a quantum router that measures and sorts:\n"
    "  |0> qubits go straight\n"
    "  |1> qubits turn clockwise\n\n"
    "Feed it superposition and you get a random 50/50 split\n"
    "into two separate paths."
)

CH3_L1 = {
    "name": "Collapse",
    "description": "Measure superposition and watch it collapse.",
    "briefing": (
        "Measurement collapses superposition!\n\n"
        "A purple (superposed) qubit becomes either red |0>\n"
        "or blue |1> with equal probability — 50/50.\n"
        "You can never predict which.\n\n"
        "Route qubits through H -> Measurement.\n"
        "The measurement gate absorbs the qubit and records\n"
        "the result in its histogram.\n\n"
        "Collapse 10 qubits to win."
    ),
    "hint": "H -> Measure: watch the histogram fill up with random results",
    "win_type": "measure",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
    },
    "locked": {(0, 2)},
    "available": [BELT, H, MEAS],
    "win_count": 10,
    "camera": (4, 2),
}

CH3_L2 = {
    "name": "Quantum Router",
    "description": "The Splitter measures and routes qubits by state.",
    "briefing": (
        "The Splitter is a quantum router. It measures\n"
        "a qubit and sends it down one of two paths:\n"
        "  |0> (red)  -> exits straight ahead\n"
        "  |1> (blue) -> turns clockwise\n\n"
        "Feed superposed qubits into the Splitter to split\n"
        "the stream 50/50. Route each output to the\n"
        "matching sink: red to the |0> sink, blue to the |1> sink.\n\n"
        "Both sinks must collect 3 qubits to win."
    ),
    "hint": "H -> Splitter sorts by state. Belt each output to its sink.",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (9, 2): (SINK, RIGHT, ZERO),
        (5, 6): (SINK, DOWN, ONE),
    },
    "locked": {(0, 2), (9, 2), (5, 6)},
    "available": [BELT, H, SPLIT],
    "win_count": 3,
    "camera": (4, 3),
}


# ---------------------------------------------------------------------------
# Chapter 4: Phase & Interference
# ---------------------------------------------------------------------------

_CH4_CONCEPT = (
    "Phase is a hidden property of superposition. You can't see\n"
    "it directly, but it determines what happens when the qubit\n"
    "is measured later.\n\n"
    "The Z gate flips the phase: |+> becomes |->. These look\n"
    "identical (both purple), but behave differently.\n\n"
    "The key insight: H -> Z -> H always produces |1>.\n"
    "The phase flip causes destructive interference —\n"
    "the |0> component cancels out. This is the foundation\n"
    "of every quantum algorithm."
)

CH4_L1 = {
    "name": "Interference",
    "description": "Discover how H -> Z -> H always produces |1>.",
    "briefing": (
        "The Z gate flips the phase of a qubit.\n"
        "You can't see phase directly, but it matters!\n\n"
        "Try this: route qubits through  H -> Z -> H.\n"
        "Something remarkable happens — the output is\n"
        "always |1>, never random.  This is interference.\n\n"
        "The sink wants blue |1> qubits.  Build the circuit!"
    ),
    "hint": "H -> Z -> H = guaranteed |1>  (interference!)",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (9, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (9, 2)},
    "available": [BELT, H, Z],
    "win_count": 5,
    "camera": (4, 2),
}

CH4_L2 = {
    "name": "Pauli Y",
    "description": "Meet the Y gate — bit flip AND phase flip in one.",
    "briefing": (
        "The Y gate is the third Pauli gate.\n\n"
        "Like X, it flips bits:  Y|0> = |1>,  Y|1> = |0>.\n"
        "Unlike X, it also flips the phase of superposition:\n"
        "  Y|+> = |−>   and   Y|−> = |+>\n\n"
        "The sink wants |1> and the generator makes |0>.\n"
        "Route the qubit through Y to flip it.\n\n"
        "Note: Y alone looks like X here — the phase difference\n"
        "only shows up in interference.  That comes next."
    ),
    "hint": "Place a Y gate on the path — it flips |0> to |1>",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (8, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (8, 2)},
    "available": [BELT, Y],
    "win_count": 5,
    "camera": (4, 2),
}

CH4_L3 = {
    "name": "Y Sandwiched",
    "description": "Two locked H gates — what do you place between them to get |1>?",
    "briefing": (
        "Two Hadamard gates are locked in place.\n"
        "Every qubit passes through both of them.\n\n"
        "H·H = identity -> if nothing is between them, you get |0> back.\n"
        "The sink wants |1>.  Just belts won't work.\n\n"
        "Experiment: what happens when Y sits between two H gates?\n"
        "  H|0> = |+>,  Y|+> = |−>,  H|−> = |1>\n\n"
        "Place Y between the two locked H gates to create\n"
        "the H·Y·H interference circuit."
    ),
    "hint": "Place one Y gate between the two locked H gates",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (3, 2): (H, RIGHT, None),
        (8, 2): (H, RIGHT, None),
        (11, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 2), (3, 2), (8, 2), (11, 2)},
    "available": [BELT, Y],
    "win_count": 5,
    "camera": (5, 2),
}


# ---------------------------------------------------------------------------
# Chapter 5: Entanglement
# ---------------------------------------------------------------------------

_CH5_CONCEPT = (
    "The CNOT gate is the first two-qubit gate you'll use.\n"
    "It spans two cells — like a real quantum circuit.\n\n"
    "Two parallel qubit streams flow through it:\n"
    "  Top  = Control (marked with a dot)\n"
    "  Bottom = Target (the gate symbol)\n\n"
    "Rule: if the control is |1>, the target gets flipped.\n"
    "Simple enough — but something magical happens when\n"
    "the control is in superposition.\n\n"
    "The target doesn't flip or not-flip — it does BOTH.\n"
    "The two qubits become entangled: measuring one\n"
    "instantly determines the other. Einstein called this\n"
    "'spooky action at a distance.'"
)

CH5_L1 = {
    "name": "Controlled Flip",
    "description": "CNOT flips the target when the control is |1>.",
    "briefing": (
        "The CNOT gate spans two cells:\n"
        "  Top row  = Control (dot)\n"
        "  Bottom row = Target (gate)\n\n"
        "Both streams flow left to right.\n"
        "The rule: if control = |1>, target gets flipped.\n"
        "  |0> -> |1>  and  |1> -> |0>\n"
        "If control = |0>, nothing happens.\n\n"
        "Both generators make |0>.  Use X on the control\n"
        "path (top) to flip it to |1>, then the CNOT will\n"
        "flip the target too.  Both sinks want |1>."
    ),
    "hint": "X on the control (top) path — CNOT flips the target",
    "pre_placed": {
        (-1, 1): (GEN, RIGHT, None),
        (-1, 2): (GEN, RIGHT, None),
        (5, 2): (CNOT, RIGHT, None),
        (9, 1): (SINK, RIGHT, ONE),
        (9, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 1), (-1, 2), (5, 2), (9, 1), (9, 2)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (4, 2),
}

CH5_L2 = {
    "name": "Bell State",
    "description": "Superposition + CNOT creates entangled pairs.",
    "briefing": (
        "Use H on the control path to create superposition.\n\n"
        "When the control is in superposition:\n"
        "  CNOT doesn't flip or not-flip — it does BOTH.\n"
        "  The two qubits become entangled.\n\n"
        "A locked Measurement gate sits on the control exit.\n"
        "When one entangled qubit is measured, watch what\n"
        "happens to its partner on the target path —\n"
        "it collapses to the same value instantly!\n\n"
        "Watch for the golden ring — it marks entanglement.\n"
        "Place the CNOT yourself."
    ),
    "hint": "H on the control (top) path, CNOT below it — watch the entanglement",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (9, 2): (MEAS, RIGHT, None),
        (9, 3): (SINK, RIGHT, None),
    },
    "locked": {(-1, 2), (-1, 3), (9, 2), (9, 3)},
    "available": [BELT, H, CNOT],
    "win_count": 5,
    "win_type": "measure",
    "camera": (4, 3),
}


# ---------------------------------------------------------------------------
# Chapter 6: Multi-Qubit Operations
# ---------------------------------------------------------------------------

_CH6_CONCEPT = (
    "Real quantum circuits use multiple qubits working together.\n\n"
    "The CZ gate applies a phase flip controlled by one qubit\n"
    "onto another. A key concept: PHASE KICKBACK.\n"
    "When a target qubit is |1> and the control is in\n"
    "superposition, the phase gets 'kicked back' onto\n"
    "the control — a trick used in most quantum algorithms.\n\n"
    "The SWAP gate exchanges the states of two qubits entirely.\n"
    "After a SWAP, each qubit carries what the other had."
)

CH6_L1 = {
    "name": "Phase Kickback",
    "description": "A |1> target kicks its phase back onto a superposition control.",
    "briefing": (
        "CZ is Controlled-Z: if the control qubit is |1>,\n"
        "it applies Z to the target.  But something stranger\n"
        "happens when the ROLES are reversed.\n\n"
        "If the TARGET is |1> and the CONTROL is in superposition:\n"
        "  the control's own phase gets flipped — |+> becomes |−>.\n"
        "This is called PHASE KICKBACK.\n\n"
        "Two parallel streams, both flowing left to right:\n"
        "  Control (top): H before CZ -> |+>\n"
        "  Target (bottom): X before CZ -> |1>\n"
        "After CZ: control is |−> — apply H to collapse it to |1>.\n"
        "Both sinks want |1>."
    ),
    "hint": "Top: H before CZ, H after CZ. Bottom: X before CZ.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (10, 2): (SINK, RIGHT, ONE),
        (10, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (10, 2), (10, 3)},
    "available": [BELT, H, X, CZ],
    "win_count": 5,
    "camera": (5, 3),
}

CH6_L2 = {
    "name": "State Exchange",
    "description": "SWAP exchanges the states of two parallel qubit streams.",
    "briefing": (
        "The SWAP gate exchanges the quantum states of two qubits.\n"
        "After a SWAP, each qubit carries the other's original state.\n\n"
        "Two parallel streams flow through a SWAP gate:\n"
        "  Top stream:    |1> (use X to flip from |0>)\n"
        "  Bottom stream: |0> (straight from the generator)\n\n"
        "After the SWAP:\n"
        "  Top exit carries the bottom stream's state -> |0>\n"
        "  Bottom exit carries the top stream's state -> |1>\n\n"
        "Route each exit to the matching sink."
    ),
    "hint": "X on the top path, SWAP in the middle, belt the exits to sinks",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (10, 2): (SINK, RIGHT, ZERO),
        (10, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (10, 2), (10, 3)},
    "available": [BELT, X, SWAP],
    "win_count": 5,
    "camera": (5, 3),
}


# ---------------------------------------------------------------------------
# Chapter 7: Interference Patterns
# ---------------------------------------------------------------------------

_CH7_CONCEPT = (
    "In Chapter 4 you learned that H→Z→H always produces |1>.\n"
    "That was a single path. Now let's use interference to CONTROL\n"
    "where qubits go.\n\n"
    "Key insight: a Splitter routes |0> straight and |1> clockwise.\n"
    "Without interference, superposition collapses randomly — 50/50.\n"
    "With interference, you decide the outcome: H→H keeps |0>,\n"
    "H→Z→H forces |1>.\n\n"
    "Combine interference with routing to build deterministic\n"
    "quantum factories."
)

CH7_L1 = {
    "name": "Taming Randomness",
    "description": "Use interference to guarantee every qubit reaches the sink.",
    "briefing": (
        "The locked Hadamard puts every qubit into superposition.\n"
        "The locked Splitter then measures them — 50/50 random.\n\n"
        "The sink only accepts |1> qubits, arriving from the\n"
        "Splitter's clockwise exit (downward).\n\n"
        "Random means ~half your qubits are wasted.\n"
        "Can you guarantee EVERY qubit reaches the sink?\n\n"
        "Hint: what happens between two Hadamard gates\n"
        "determines the outcome."
    ),
    "hint": "H → Z → H = always |1> → Splitter sends all down",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (3, 3): (H, RIGHT, None),
        (9, 3): (SPLIT, RIGHT, None),
        (9, 7): (SINK, DOWN, ONE),
    },
    "locked": {(0, 3), (3, 3), (9, 3), (9, 7)},
    "available": [BELT, H, Z],
    "win_count": 5,
    "camera": (5, 4),
}

CH7_L2 = {
    "name": "Both Ways",
    "description": "Master constructive AND destructive interference.",
    "briefing": (
        "Two assembly lines, each with a locked Hadamard\n"
        "and a locked Splitter.\n\n"
        "Top sink wants |0> (exits straight from Splitter).\n"
        "Bottom sink wants |1> (exits clockwise from Splitter).\n\n"
        "Use constructive interference (H·H = identity) on the\n"
        "top path to keep qubits as |0>.\n\n"
        "Use destructive interference (H·Z·H) on the bottom\n"
        "path to flip qubits to |1>."
    ),
    "hint": "Top: add H before Splitter. Bottom: add Z then H.",
    "pre_placed": {
        (0, 1): (GEN, RIGHT, None),
        (3, 1): (H, RIGHT, None),
        (9, 1): (SPLIT, RIGHT, None),
        (13, 1): (SINK, RIGHT, ZERO),
        (0, 5): (GEN, RIGHT, None),
        (3, 5): (H, RIGHT, None),
        (9, 5): (SPLIT, RIGHT, None),
        (9, 9): (SINK, DOWN, ONE),
    },
    "locked": {(0, 1), (3, 1), (9, 1), (13, 1),
               (0, 5), (3, 5), (9, 5), (9, 9)},
    "available": [BELT, H, Z],
    "win_count": 5,
    "camera": (6, 4),
}

CH7_L3 = {
    "name": "Interference Lab",
    "description": "Three lanes, three targets — pick the right tool for each.",
    "briefing": (
        "Three generators, three sinks, three target states.\n\n"
        "  Top:     deliver |1>\n"
        "  Middle:  deliver |0>\n"
        "  Bottom:  deliver |1>\n\n"
        "You have every single-qubit gate. Some paths need\n"
        "interference, others just need the right gate.\n\n"
        "Find the most efficient solution for each lane."
    ),
    "hint": "Top: H→Z→H or just X. Middle: belts only. Bottom: Y or X.",
    "pre_placed": {
        (0, 1): (GEN, RIGHT, None),
        (11, 1): (SINK, RIGHT, ONE),
        (0, 5): (GEN, RIGHT, None),
        (11, 5): (SINK, RIGHT, ZERO),
        (0, 9): (GEN, RIGHT, None),
        (11, 9): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 1), (11, 1), (0, 5), (11, 5), (0, 9), (11, 9)},
    "available": [BELT, H, X, Y, Z],
    "win_count": 5,
    "camera": (5, 5),
}


# ---------------------------------------------------------------------------
# Chapter 8: Quantum Circuits
# ---------------------------------------------------------------------------

_CH8_CONCEPT = (
    "Real quantum circuits combine single-qubit and two-qubit gates\n"
    "into larger patterns with surprising properties.\n\n"
    "A key equivalence: sandwiching CZ between two Hadamard gates\n"
    "on the target makes it behave exactly like CNOT.\n"
    "This is because H converts phase flips into bit flips.\n\n"
    "Understanding circuit equivalences is the foundation of\n"
    "quantum algorithm design — there are always multiple ways\n"
    "to build the same computation."
)

CH8_L1 = {
    "name": "Circuit Equivalence",
    "description": "Build a CNOT from CZ and Hadamard gates.",
    "briefing": (
        "CZ only flips phase — never directly flips bits.\n"
        "But H converts phase flips into bit flips!\n\n"
        "The equivalence: H → CZ → H on the target path\n"
        "behaves exactly like CNOT.\n\n"
        "Both sinks want |1>.\n"
        "  Control (top): use X to make |1>\n"
        "  Target (bottom): H before CZ, H after CZ\n\n"
        "The |1> control triggers CZ's phase flip,\n"
        "and the surrounding H gates convert it to a bit flip."
    ),
    "hint": "Top: X. Bottom: H before and after the CZ.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (5, 3): (CZ, RIGHT, None),
        (10, 2): (SINK, RIGHT, ONE),
        (10, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (5, 3), (10, 2), (10, 3)},
    "available": [BELT, H, X],
    "win_count": 5,
    "camera": (5, 3),
}

CH8_L2 = {
    "name": "Entanglement Chain",
    "description": "Chain entanglement across three qubits with two CNOTs.",
    "briefing": (
        "Three parallel qubit streams, two CNOTs.\n\n"
        "Use H on the top stream, then route it through\n"
        "two CNOT control inputs. Each CNOT entangles its\n"
        "control with its target.\n\n"
        "The top stream is control for the first CNOT.\n"
        "Route its output down to be control for the second.\n"
        "When the Measurement gate collapses one qubit,\n"
        "watch all three snap to the same value."
    ),
    "hint": "H on top, CNOT1 links top+middle, route top down to CNOT2 for middle+bottom.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 4): (GEN, RIGHT, None),
        (-1, 6): (GEN, RIGHT, None),
        (12, 2): (MEAS, RIGHT, None),
        (12, 4): (SINK, RIGHT, None),
        (12, 6): (SINK, RIGHT, None),
    },
    "locked": {(-1, 2), (-1, 4), (-1, 6), (12, 2), (12, 4), (12, 6)},
    "available": [BELT, H, CNOT],
    "win_count": 5,
    "win_type": "measure",
    "camera": (5, 4),
}


# ---------------------------------------------------------------------------
# Chapter 9: Quantum Noise
# ---------------------------------------------------------------------------

_CH9_CONCEPT = (
    "Real quantum computers suffer from noise — random errors\n"
    "that corrupt qubits. A perfect qubit can spontaneously\n"
    "flip from |0> to |1> or vice versa.\n\n"
    "The Noise gate simulates this: each qubit passing through\n"
    "has a 50% chance of being flipped. The corruption is\n"
    "completely random and unpredictable.\n\n"
    "Your first defense: avoid the noise entirely.\n"
    "Route your qubits around noisy channels whenever possible."
)

CH9_L1 = {
    "name": "Noisy Channel",
    "description": "The direct path is corrupted — find a way around.",
    "briefing": (
        "A Noise gate sits on the direct path from\n"
        "generator to sink. Every qubit passing through\n"
        "has a 50% chance of being flipped.\n\n"
        "The sink wants |0> but noise randomly changes\n"
        "some qubits to |1>.\n\n"
        "Build a detour — route your qubits AROUND the\n"
        "noise gate to guarantee clean delivery."
    ),
    "hint": "Build a belt path that bypasses the Noise gate.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (4, 3): (NOISE, RIGHT, None),
        (8, 3): (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 3), (4, 3), (8, 3)},
    "available": [BELT],
    "win_count": 5,
    "camera": (4, 3),
}

CH9_L2 = {
    "name": "Noise Breaks Everything",
    "description": "Noise destroys interference — see the damage firsthand.",
    "briefing": (
        "Two assembly lines, both with H gates for interference.\n\n"
        "Top line: clean. H → Z → H produces |1> reliably.\n"
        "Bottom line: a locked Noise gate sits between\n"
        "the Z and the second H. Noise randomizes the phase,\n"
        "breaking the interference pattern.\n\n"
        "Both sinks want |1>.\n"
        "Top line works perfectly.\n"
        "Bottom line: route AROUND the noise to save it."
    ),
    "hint": "Top: H→Z→H as normal. Bottom: bypass the Noise gate.",
    "pre_placed": {
        (0, 1): (GEN, RIGHT, None),
        (12, 1): (SINK, RIGHT, ONE),
        (0, 6): (GEN, RIGHT, None),
        (5, 6): (NOISE, RIGHT, None),
        (12, 6): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 1), (12, 1), (0, 6), (5, 6), (12, 6)},
    "available": [BELT, H, Z],
    "win_count": 5,
    "camera": (6, 3),
}

CH9_L3 = {
    "name": "Noisy Crossroads",
    "description": "Multiple noise gates block the paths — find the one clean route.",
    "briefing": (
        "Noise gates are everywhere! Three of the four\n"
        "possible paths from generator to sink pass\n"
        "through locked Noise gates.\n\n"
        "Find the ONE clean path and route your qubits\n"
        "through it. The sink wants |0>."
    ),
    "hint": "Only one path has no Noise gate — try going down first.",
    "pre_placed": {
        (0, 0): (GEN, RIGHT, None),
        (3, 0): (NOISE, RIGHT, None),
        (0, 3): (NOISE, DOWN, None),
        (6, 3): (NOISE, RIGHT, None),
        (9, 5): (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 0), (3, 0), (0, 3), (6, 3), (9, 5)},
    "available": [BELT],
    "win_count": 5,
    "camera": (4, 2),
}


# ---------------------------------------------------------------------------
# Chapter 10: Error Detection
# ---------------------------------------------------------------------------

_CH10_CONCEPT = (
    "You can't always avoid noise. But you CAN detect it.\n\n"
    "The trick: send two identical qubits down parallel paths.\n"
    "One path passes through noise, the other stays clean.\n"
    "At the end, a CNOT compares them.\n\n"
    "If noise flipped the qubit, the CNOT's control output\n"
    "changes — revealing the error. A Splitter then routes\n"
    "corrupted qubits away from the output.\n\n"
    "This is the core idea behind quantum error detection:\n"
    "redundancy and comparison."
)

CH10_L1 = {
    "name": "Parity Check",
    "description": "Use CNOT to detect whether noise flipped a qubit.",
    "briefing": (
        "Two generators both produce |0>.\n"
        "One qubit passes through a locked Noise gate.\n"
        "The other stays clean.\n\n"
        "They meet at a CNOT:\n"
        "  Clean qubit = control (from top)\n"
        "  Noisy qubit = target (from left)\n\n"
        "If noise did nothing: control stays |0>.\n"
        "If noise flipped: control becomes |1>.\n\n"
        "The Measurement gate records the parity check.\n"
        "Build the circuit and watch the error detection!"
    ),
    "hint": "Connect clean gen to CNOT control (top), noisy gen to target (left).",
    "win_type": "measure",
    "pre_placed": {
        (5, -1): (GEN, DOWN, None),
        (-1, 3): (GEN, RIGHT, None),
        (2, 3): (NOISE, RIGHT, None),
        (9, 3): (SINK, RIGHT, None),
        (5, 8): (MEAS, DOWN, None),
    },
    "locked": {(5, -1), (-1, 3), (2, 3), (9, 3), (5, 8)},
    "available": [BELT, CNOT],
    "win_count": 10,
    "camera": (5, 3),
}

CH10_L2 = {
    "name": "Error Filter",
    "description": "Detect noise errors AND discard corrupted qubits.",
    "briefing": (
        "Same setup as before, but now we FILTER the output.\n\n"
        "After the CNOT compares clean and noisy qubits,\n"
        "feed the target into a Splitter:\n"
        "  |0> (uncorrupted) → straight to the sink\n"
        "  |1> (corrupted)   → discarded\n\n"
        "The sink wants |0>. Only clean qubits should\n"
        "reach it. Corrupted qubits go to the discard path.\n\n"
        "Place the CNOT and Splitter to build the filter."
    ),
    "hint": "CNOT at the crossing, Splitter after target exit. |0> to sink.",
    "pre_placed": {
        (5, -1): (GEN, DOWN, None),
        (-1, 3): (GEN, RIGHT, None),
        (2, 3): (NOISE, RIGHT, None),
        (13, 3): (SINK, RIGHT, ZERO),
    },
    "locked": {(5, -1), (-1, 3), (2, 3), (13, 3)},
    "available": [BELT, CNOT, SPLIT],
    "win_count": 5,
    "camera": (6, 3),
}


# ---------------------------------------------------------------------------
# Chapter 11: Deutsch's Problem
# ---------------------------------------------------------------------------

_CH11_CONCEPT = (
    "Imagine a black box — an Oracle — that computes a function.\n"
    "You can't look inside. It's either CONSTANT (always does\n"
    "nothing) or BALANCED (always flips the phase).\n\n"
    "Classically, you'd need to test both inputs to be sure.\n"
    "Quantumly: send a superposed qubit through H → Oracle → H.\n"
    "The output is deterministic:\n"
    "  Constant oracle → |0>  (constructive interference)\n"
    "  Balanced oracle → |1>  (destructive interference)\n\n"
    "One query. Certain answer. This is Deutsch's algorithm —\n"
    "the first proof that quantum beats classical."
)

CH11_L1 = {
    "name": "The Constant Oracle",
    "description": "A black-box that does nothing — detect it with one query.",
    "briefing": (
        "The locked Oracle gate is a black box.\n"
        "This one is CONSTANT — it does nothing to qubits.\n\n"
        "Build the detection circuit: H → Oracle → H\n\n"
        "A constant oracle preserves interference:\n"
        "  H|0> = |+> → Oracle(nothing) → |+> → H → |0>\n\n"
        "The sink wants |0>. Build the circuit!"
    ),
    "hint": "Place H before and after the Oracle. Output is always |0>.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (5, 3): (ORA_C, RIGHT, None),
        (10, 3): (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 3), (5, 3), (10, 3)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (5, 3),
}

CH11_L2 = {
    "name": "The Balanced Oracle",
    "description": "This oracle flips the phase — detect it with one query.",
    "briefing": (
        "Same circuit, different oracle.\n"
        "This one is BALANCED — it flips the phase.\n\n"
        "Build H → Oracle → H again:\n"
        "  H|0> = |+> → Oracle(phase flip) → |-> → H → |1>\n\n"
        "The destructive interference reveals the oracle type!\n"
        "The sink wants |1>."
    ),
    "hint": "Same circuit as before — H, Oracle, H. Output is now |1>.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (5, 3): (ORA_B, RIGHT, None),
        (10, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 3), (5, 3), (10, 3)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (5, 3),
}

CH11_L3 = {
    "name": "Oracle Classifier",
    "description": "Two unknown oracles — classify both automatically.",
    "briefing": (
        "Two oracles, two assembly lines.\n"
        "You don't need to know which is which!\n\n"
        "Build H → Oracle → H → Splitter on each line.\n"
        "The Splitter routes by state:\n"
        "  |0> (constant) → straight to the |0> sink\n"
        "  |1> (balanced) → clockwise to the |1> sink\n\n"
        "The circuit automatically classifies the oracle.\n"
        "This is the power of Deutsch's algorithm."
    ),
    "hint": "H before each Oracle, H after, then Splitter sorts the answer.",
    "pre_placed": {
        (0, 1): (GEN, RIGHT, None),
        (5, 1): (ORA_C, RIGHT, None),
        (11, 1): (SPLIT, RIGHT, None),
        (15, 1): (SINK, RIGHT, ZERO),
        (0, 6): (GEN, RIGHT, None),
        (5, 6): (ORA_B, RIGHT, None),
        (11, 6): (SPLIT, RIGHT, None),
        (11, 10): (SINK, DOWN, ONE),
    },
    "locked": {(0, 1), (5, 1), (11, 1), (15, 1),
               (0, 6), (5, 6), (11, 6), (11, 10)},
    "available": [BELT, H],
    "win_count": 5,
    "camera": (7, 4),
}


# ---------------------------------------------------------------------------
# Chapter 12: Quantum Cloning
# ---------------------------------------------------------------------------

_CH12_CONCEPT = (
    "The No-Cloning Theorem says you cannot perfectly copy an\n"
    "unknown quantum state. But classical states (|0> and |1>)\n"
    "CAN be copied — only superposition is forbidden.\n\n"
    "The Duplicator gate makes a copy of any qubit:\n"
    "  Original exits straight (gate direction)\n"
    "  Copy exits clockwise (perpendicular)\n\n"
    "If the input is in superposition, the Duplicator collapses\n"
    "it first — you get two identical classical copies, not two\n"
    "entangled qubits. This is the no-cloning limit in action."
)

CH12_L1 = {
    "name": "The Duplicator",
    "description": "One qubit in, two copies out.",
    "briefing": (
        "The Duplicator sends a copy of each qubit in\n"
        "two directions:\n"
        "  Straight → original continues forward\n"
        "  Clockwise → copy goes perpendicular\n\n"
        "Both sinks want |0>. The generator makes |0>.\n"
        "Connect the Duplicator's outputs to both sinks."
    ),
    "hint": "Belt from straight exit to right sink, CW exit to bottom sink.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (4, 3): (DUP, RIGHT, None),
        (8, 3): (SINK, RIGHT, ZERO),
        (4, 7): (SINK, DOWN, ZERO),
    },
    "locked": {(0, 3), (4, 3), (8, 3), (4, 7)},
    "available": [BELT],
    "win_count": 5,
    "camera": (4, 4),
}

CH12_L2 = {
    "name": "Redundant Channel",
    "description": "Duplicate before noise — the backup always gets through.",
    "briefing": (
        "The Duplicator creates a backup copy before the\n"
        "noisy channel.\n\n"
        "Original path: through the locked Noise gate.\n"
        "  Use a Splitter to filter: |0> to the sink,\n"
        "  |1> (corrupted) gets discarded.\n\n"
        "Copy path: clean detour straight to a second sink.\n\n"
        "Both sinks want |0>. The backup guarantees output\n"
        "even when noise strikes."
    ),
    "hint": "Splitter after noise filters corrupted qubits. Copy path goes clean.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (3, 3): (DUP, RIGHT, None),
        (6, 3): (NOISE, RIGHT, None),
        (12, 3): (SINK, RIGHT, ZERO),
        (3, 7): (SINK, DOWN, ZERO),
    },
    "locked": {(0, 3), (3, 3), (6, 3), (12, 3), (3, 7)},
    "available": [BELT, SPLIT],
    "win_count": 5,
    "camera": (6, 4),
}


# ---------------------------------------------------------------------------
# Chapter 13: Grand Challenge
# ---------------------------------------------------------------------------

_CH13_CONCEPT = (
    "Time to combine everything you've learned.\n\n"
    "These puzzles require multiple concepts working together:\n"
    "bit flips, phase kicks, entanglement, interference,\n"
    "noise avoidance, and clever routing.\n\n"
    "There's no single trick — you need to read the board,\n"
    "understand what each sink needs, and build the right\n"
    "circuit for each path."
)

CH13_L1 = {
    "name": "Quantum Lab",
    "description": "Three generators, three sinks — SWAP, interference, and routing.",
    "briefing": (
        "Two parallel streams cross at a locked SWAP gate.\n\n"
        "SWAP exchanges the states of the two qubits\n"
        "passing through it. Plan ahead:\n"
        "  What state enters control (top)?\n"
        "  What state enters target (bottom)?\n\n"
        "The third stream is independent — it needs\n"
        "superposition.\n\n"
        "  Sink A (control exit): wants |0>\n"
        "  Sink B (target exit): wants |1>\n"
        "  Sink C (third path): wants superposition"
    ),
    "hint": "X on the top path, SWAP exchanges states. H on the third path.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (0, 4): (GEN, RIGHT, None),
        (0, 8): (GEN, RIGHT, None),
        (5, 4): (SWAP, RIGHT, None),
        (11, 3): (SINK, RIGHT, ZERO),
        (11, 4): (SINK, RIGHT, ONE),
        (11, 8): (SINK, RIGHT, SUP),
    },
    "locked": {(0, 3), (0, 4), (0, 8), (5, 4), (11, 3), (11, 4), (11, 8)},
    "available": [BELT, H, X],
    "win_count": 5,
    "camera": (5, 4),
}

CH13_L2 = {
    "name": "Double Flip",
    "description": "Two CNOTs in sequence — trace the state through both.",
    "briefing": (
        "Two locked CNOT gates in a chain.\n"
        "Three parallel streams:\n\n"
        "  Top:    control of first CNOT, exits right\n"
        "  Middle: target of first, control of second\n"
        "  Bottom: target of second CNOT\n\n"
        "Use X on the top path to flip control to |1>.\n"
        "First CNOT flips middle to |1>.\n"
        "Middle feeds second CNOT's control.\n"
        "Second CNOT flips bottom to |1>.\n"
        "All three sinks want |1>."
    ),
    "hint": "X on the top path — the flip cascades through both CNOTs.",
    "pre_placed": {
        (-1, 1): (GEN, RIGHT, None),
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (4, 2): (CNOT, RIGHT, None),
        (8, 3): (CNOT, RIGHT, None),
        (12, 1): (SINK, RIGHT, ONE),
        (12, 2): (SINK, RIGHT, ONE),
        (12, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 1), (-1, 2), (-1, 3), (4, 2), (8, 3),
               (12, 1), (12, 2), (12, 3)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (5, 2),
}


# ---------------------------------------------------------------------------
# Chapter 14: Quantum Mastery
# ---------------------------------------------------------------------------

_CH14_CONCEPT = (
    "You've mastered every gate in the factory.\n\n"
    "These final challenges combine noise avoidance,\n"
    "interference, phase kickback, and entanglement\n"
    "into puzzles that require deep understanding.\n\n"
    "No new tools — just everything you've learned,\n"
    "pushed to the limit."
)

CH14_L1 = {
    "name": "Noisy Interference",
    "description": "Noise blocks interference — use a Splitter to recover.",
    "briefing": (
        "The generator feeds through locked H and Z gates\n"
        "for interference, but a Noise gate sits after Z.\n\n"
        "Without noise: H → Z → H = always |1>.\n"
        "With noise: the phase flip is randomly undone,\n"
        "giving a 50/50 mix of |0> and |1>.\n\n"
        "Use a Splitter after the second H to catch the\n"
        "|1> qubits that survived. The sink wants |1>."
    ),
    "hint": "Build: H(locked) → Z(locked) → Noise(locked) → H → Splitter → |1> CW to sink.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (2, 3): (H, RIGHT, None),
        (4, 3): (Z, RIGHT, None),
        (6, 3): (NOISE, RIGHT, None),
        (13, 7): (SINK, DOWN, ONE),
    },
    "locked": {(0, 3), (2, 3), (4, 3), (6, 3), (13, 7)},
    "available": [BELT, H, SPLIT],
    "win_count": 5,
    "camera": (7, 4),
}

CH14_L2 = {
    "name": "Kickback Detour",
    "description": "Phase kickback through a noisy landscape.",
    "briefing": (
        "The control path passes through a locked Noise gate.\n"
        "You need |1> on that path for phase kickback\n"
        "to work on the CZ gate.\n\n"
        "Route the control qubit AROUND the noise,\n"
        "apply X to flip it to |1>, then let CZ do\n"
        "its phase kickback on the target qubit.\n\n"
        "Target (bottom): H before CZ, H after CZ → |1>.\n"
        "Control (top): X, detour around noise → |1>.\n"
        "Both sinks want |1>."
    ),
    "hint": "Detour top gen around noise. X for |1>. H-CZ-H on bottom path.",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (-1, 4): (GEN, RIGHT, None),
        (2, 3): (NOISE, RIGHT, None),
        (5, 4): (CZ, RIGHT, None),
        (11, 3): (SINK, RIGHT, ONE),
        (11, 4): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 3), (-1, 4), (2, 3), (5, 4), (11, 3), (11, 4)},
    "available": [BELT, H, X],
    "win_count": 5,
    "camera": (5, 4),
}


# ---------------------------------------------------------------------------
# Chapter definitions
# ---------------------------------------------------------------------------

CHAPTERS = [
    {
        "name": "Classical Foundations",
        "subtitle": "Binary signals and logic gates",
        "concept": _CH1_CONCEPT,
        "color": (100, 220, 120),
        "levels": [CH1_L1, CH1_L2, CH1_L3],
    },
    {
        "name": "Superposition",
        "subtitle": "Both 0 and 1 at the same time",
        "concept": _CH2_CONCEPT,
        "color": (190, 135, 255),
        "levels": [CH2_L1, CH2_L2, CH2_L3],
    },
    {
        "name": "Measurement",
        "subtitle": "Collapsing quantum states",
        "concept": _CH3_CONCEPT,
        "color": (255, 214, 112),
        "levels": [CH3_L1, CH3_L2],
    },
    {
        "name": "Phase & Interference",
        "subtitle": "The hidden property that powers quantum computing",
        "concept": _CH4_CONCEPT,
        "color": (240, 120, 180),
        "levels": [CH4_L1, CH4_L2, CH4_L3],
    },
    {
        "name": "Entanglement",
        "subtitle": "Spooky action at a distance",
        "concept": _CH5_CONCEPT,
        "color": (255, 200, 60),
        "levels": [CH5_L1, CH5_L2],
    },
    {
        "name": "Multi-Qubit Ops",
        "subtitle": "Phase kickback and state exchange",
        "concept": _CH6_CONCEPT,
        "color": (90, 220, 230),
        "levels": [CH6_L1, CH6_L2],
    },
    {
        "name": "Interference Patterns",
        "subtitle": "Controlling randomness with interference",
        "concept": _CH7_CONCEPT,
        "color": (130, 200, 255),
        "levels": [CH7_L1, CH7_L2, CH7_L3],
    },
    {
        "name": "Quantum Circuits",
        "subtitle": "Gate equivalences and entanglement chains",
        "concept": _CH8_CONCEPT,
        "color": (180, 255, 180),
        "levels": [CH8_L1, CH8_L2],
    },
    {
        "name": "Quantum Noise",
        "subtitle": "Random errors and how to avoid them",
        "concept": _CH9_CONCEPT,
        "color": (200, 70, 70),
        "levels": [CH9_L1, CH9_L2, CH9_L3],
    },
    {
        "name": "Error Detection",
        "subtitle": "Finding and filtering quantum errors",
        "concept": _CH10_CONCEPT,
        "color": (255, 180, 100),
        "levels": [CH10_L1, CH10_L2],
    },
    {
        "name": "Deutsch's Problem",
        "subtitle": "The first quantum speedup",
        "concept": _CH11_CONCEPT,
        "color": (160, 100, 220),
        "levels": [CH11_L1, CH11_L2, CH11_L3],
    },
    {
        "name": "Quantum Cloning",
        "subtitle": "Copying qubits and the no-cloning limit",
        "concept": _CH12_CONCEPT,
        "color": (100, 200, 140),
        "levels": [CH12_L1, CH12_L2],
    },
    {
        "name": "Grand Challenge",
        "subtitle": "Combining every concept",
        "concept": _CH13_CONCEPT,
        "color": (220, 200, 100),
        "levels": [CH13_L1, CH13_L2],
    },
    {
        "name": "Quantum Mastery",
        "subtitle": "The final exam",
        "concept": _CH14_CONCEPT,
        "color": (255, 255, 255),
        "levels": [CH14_L1, CH14_L2],
    },
]

# Flat list for backwards compatibility (completion tracking uses global indices)
ALL_LEVELS = []
for _ch in CHAPTERS:
    ALL_LEVELS.extend(_ch["levels"])


def chapter_level_offset(ch_idx):
    return sum(len(CHAPTERS[i]["levels"]) for i in range(ch_idx))
