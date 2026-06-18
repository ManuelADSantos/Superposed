"""Campaign content: chapters and levels.

Each chapter groups related levels, provides a concept explanation,
and specifies which gates are unlocked at that point in the progression.
ALL_LEVELS is derived by flattening all chapter level lists — global indices
remain stable for completion tracking.
"""

from __future__ import annotations

from ..core.entities import Direction as D, QubitState as Q

UP, RIGHT, DOWN, LEFT = D.UP, D.RIGHT, D.DOWN, D.LEFT
ZERO, ONE = Q.ZERO, Q.ONE
PLUS, MINUS, PLUS_I, MINUS_I = Q.PLUS, Q.MINUS, Q.PLUS_I, Q.MINUS_I

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
MEAS = "measurement"
SPLIT = "splitter"
NOISE = "noise"


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
        (7, 2): (SINK, RIGHT, PLUS),
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
        (9, 8): (SINK, RIGHT, PLUS),
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
        (9, 5): (SINK, RIGHT, PLUS),
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
        (4, 2): (MEAS, RIGHT, None),
        (2,2): (H, RIGHT, None),
    },
    "locked": {(0, 2), (4, 2), (2, 2)},
    "available": [BELT],
    "win_count": 10,
    "camera": (3, 2),
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
        "Both sinks must collect 10 qubits to win."
    ),
    "hint": "H -> Splitter sorts by state. Belt each output to its sink.",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (5, -1): (SINK, RIGHT, ZERO),
        (5, 5): (SINK, DOWN, ONE),
    },
    "locked": {(0, 2), (5, -1), (5, 5)},
    "available": [BELT, H, SPLIT],
    "win_count": 10,
    "camera": (4, 2),
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
        "Watch the tick on the qubit ring — Z rotates it 180°.\n\n"
        "Route qubits through  H -> Z -> H.\n"
        "H creates |+>, Z flips its phase to |->.\n"
        "The second H converts that phase difference into\n"
        "a bit flip: |-> always becomes |1>, never random.\n\n"
        "This is interference — the phase is consumed\n"
        "by the second H to produce a deterministic output.\n\n"
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
        "Like X, it flips bits. Unlike X, it also flips\n"
        "the phase of a superposition:\n"
        "  Y|+> = |−>   and   Y|−> = |+>\n\n"
        "A locked H gate puts the qubit into |+>.\n"
        "The sink wants |−> — a superposition with the phase\n"
        "tick pointing left (180°).\n"
        "Place Y after H to flip the phase."
    ),
    "hint": "H makes |+>, Y flips it to |−> — match the phase tick.",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (2, 2): (H, RIGHT, None),
        (9, 2): (SINK, RIGHT, MINUS),
    },
    "locked": {(0, 2), (2, 2), (9, 2)},
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
        (0, 2): (BELT, RIGHT, None),
        (1, 2): (BELT, RIGHT, None),
        (2, 2): (BELT, RIGHT, None),
        (3, 2): (BELT, RIGHT, None),
        (4, 2): (BELT, RIGHT, None),
        (5, 2): (CNOT, RIGHT, None),
        (6, 2): (BELT, RIGHT, None),
        (7, 2): (BELT, RIGHT, None),
        (8, 2): (BELT, RIGHT, None),
        (9, 1): (SINK, RIGHT, ONE),
        (9, 2): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 1), (-1, 2),
               (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
               (5, 2), (6, 2), (7, 2), (8, 2),
               (9, 1), (9, 2)},
    "available": [BELT, X],
    "gate_limits": {X: 1},
    "win_count": 5,
    "camera": (4, 2),
}

CH5_L2 = {
    "name": "Bell State",
    "description": "Superposition + CNOT creates entangled pairs.",
    "briefing": (
        "Create entangled pairs with H + CNOT, then\n"
        "measure BOTH qubits to see the correlation.\n\n"
        "Place two Measurement gates — one on each path,\n"
        "one block apart. The first measurement collapses\n"
        "the entangled pair. The second measures the partner\n"
        "that was instantly determined.\n\n"
        "Watch for the golden ring — it marks entanglement.\n"
        "Both qubits always collapse to matching values!"
    ),
    "hint": "H on control, CNOT to entangle, MEAS on both paths side by side",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
    },
    "locked": {(-1, 2), (-1, 3)},
    "available": [BELT, H, CNOT, MEAS],
    "win_count": 10,
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
        "  Top stream:    |1> (straight from the generator)\n"
        "  Bottom stream: |0> (straight from the generator)\n\n"
        "After the SWAP:\n"
        "  Top exit carries the bottom stream's state -> |0>\n"
        "  Bottom exit carries the top stream's state -> |1>\n\n"
        "Route each exit to the matching sink."
    ),
    "hint": "SWAP in the middle, then belt the exits to matching sinks",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (0, 2): (X, RIGHT, None),
        (3, 2): (SINK, RIGHT, ZERO),
        (3, 3): (SINK, RIGHT, ONE),

    },
    "unlocked": {(1, 2), (2, 2),(0, 3), (1, 3), (2, 3)},
    
    "available": [BELT, SWAP],
    "gate_limits": {SWAP: 1},
    "win_count": 10,
    "camera": (2, 3),
}


# ---------------------------------------------------------------------------
# Chapter 7: Interference Patterns
# ---------------------------------------------------------------------------

_CH7_CONCEPT = (
    "In Chapter 4 you learned that H→Z→H always produces |1>.\n"
    "That was a single path. Now let's use interference to CONTROL\n"
    "where qubits go.\n\n"
    "Key insight: a Splitter routes |0> up and |1> down.\n"
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
        "The locked Splitter routes |0> up and |1> down.\n\n"
        "The sink below accepts |1> qubits.\n\n"
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
        "Splitter routes |0> up and |1> down.\n"
        "Top sink (above) wants |0>.\n"
        "Bottom sink (below) wants |1>.\n\n"
        "Use constructive interference (H·H = identity) on the\n"
        "top path to keep qubits as |0>.\n\n"
        "Use destructive interference (H·Z·H) on the bottom\n"
        "path to flip qubits to |1>."
    ),
    "hint": "Top: add H before Splitter. Bottom: add Z then H.",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (3, 2): (H, RIGHT, None),
        (9, 2): (SPLIT, RIGHT, None),
        (9, 1): (SINK, DOWN, ZERO),
        (0, 6): (GEN, RIGHT, None),
        (3, 6): (H, RIGHT, None),
        (9, 6): (SPLIT, RIGHT, None),
        (9, 9): (SINK, DOWN, ONE),
    },
    "locked": {(0, 2), (3, 2), (9, 2), (9, 1),
               (0, 6), (3, 6), (9, 6), (9, 9)},
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
        (7, 1): (SINK, RIGHT, ONE),
        (0, 3): (GEN, RIGHT, None),
        (7, 3): (SINK, RIGHT, ZERO),
        (0, 5): (GEN, RIGHT, None),
        (7, 5): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 1), (7, 1), (0, 3), (7, 3), (0, 5), (7, 5)},
    "available": [BELT, H, X, Y, Z],
    "win_count": 5,
    "camera": (3, 3),
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
        (4, 3): (CZ, RIGHT, None),
        (8, 2): (SINK, RIGHT, ONE),
        (8, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (4, 3), (8, 2), (8, 3)},
    "available": [BELT, H, X],
    "win_count": 5,
    "camera": (4, 3),
}

CH8_L2 = {
    "name": "Entanglement Chain",
    "description": "Chain entanglement across three qubits with two CNOTs.",
    "briefing": (
        "Three parallel streams, three sinks — all want |1>.\n"
        "You only have ONE Hadamard gate.\n\n"
        "H alone converts one stream, but the others stay |0>.\n"
        "Use CNOT to chain entanglement across all three:\n"
        "  when the H-qubit collapses to |1>,\n"
        "  all entangled partners become |1> too.\n\n"
        "Place H on one stream, then CNOT-chain the others.\n"
        "About half the waves will match — that's expected."
    ),
    "hint": "H on one path, CNOT1 to entangle with second, CNOT2 to chain to third.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (-1, 4): (GEN, RIGHT, None),
        (9, 2): (SINK, RIGHT, ONE),
        (9, 3): (SINK, RIGHT, ONE),
        (9, 4): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (-1, 4), (9, 2), (9, 3), (9, 4)},
    "available": [BELT, H, CNOT],
    "gate_limits": {H: 1},
    "win_count": 3,
    "camera": (4, 3),
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
        (5, 0): (GEN, DOWN, None),
        (-1, 3): (GEN, RIGHT, None),
        (2, 3): (NOISE, RIGHT, None),
        (8, 3): (SINK, RIGHT, None),
        (5, 6): (MEAS, DOWN, None),
    },
    "locked": {(5, 0), (-1, 3), (2, 3), (8, 3), (5, 6)},
    "available": [BELT, CNOT],
    "gate_limits": {CNOT: 1},
    "win_count": 10,
    "camera": (4, 3),
}

CH10_L2 = {
    "name": "Error Filter",
    "description": "Detect noise errors AND discard corrupted qubits.",
    "briefing": (
        "Same setup as before, but now we FILTER the output.\n\n"
        "After the CNOT compares clean and noisy qubits,\n"
        "feed the target into a Splitter:\n"
        "  |0> (uncorrupted) → exits up to the sink\n"
        "  |1> (corrupted)   → exits down, discarded\n\n"
        "The sink wants |0>. Only clean qubits should\n"
        "reach it. Corrupted qubits go to the discard path.\n\n"
        "Place the CNOT and Splitter to build the filter."
    ),
    "hint": "CNOT at the crossing, Splitter after target exit. |0> up to sink.",
    "pre_placed": {
        (5, 0): (GEN, DOWN, None),
        (-1, 3): (GEN, RIGHT, None),
        (2, 3): (NOISE, RIGHT, None),
        (8, 2): (SINK, RIGHT, ZERO),
    },
    "locked": {(5, 0), (-1, 3), (2, 3), (8, 2)},
    "available": [BELT, CNOT, SPLIT],
    "win_count": 5,
    "camera": (4, 2),
}


# ---------------------------------------------------------------------------
# Chapter 11: Deutsch's Problem
# ---------------------------------------------------------------------------

_CH11_CONCEPT = (
    "Deutsch's algorithm distinguishes two kinds of functions:\n"
    "CONSTANT functions leave interference constructive,\n"
    "while BALANCED functions flip phase and make interference\n"
    "destructive.\n\n"
    "In this factory, you build those function blocks yourself:\n"
    "  Constant = no phase flip\n"
    "  Balanced = Z phase flip\n\n"
    "Send a superposed qubit through H → function → H.\n"
    "The output is deterministic:\n"
    "  Constant -> |0>  (constructive interference)\n"
    "  Balanced -> |1>  (destructive interference)"
)

CH11_L2 = {
    "name": "Balanced Function",
    "description": "Build the balanced Deutsch case with Z.",
    "briefing": (
        "A balanced function flips phase.\n\n"
        "Build the Deutsch detection circuit with Z in the middle:\n"
        "  H -> Z -> H\n\n"
        "The first H creates |+>. Z turns it into |->.\n"
        "The final H converts that phase difference into |1>."
    ),
    "hint": "H -> Z -> H gives guaranteed |1>.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (7, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(0, 3), (7, 3)},
    "available": [BELT, H, Z],
    "gate_limits": {H: 2, Z: 1},
    "win_count": 5,
    "camera": (3, 3),
}

CH11_L3 = {
    "name": "Deutsch Classifier",
    "description": "Build constant and balanced paths, then route the answers.",
    "briefing": (
        "Now build both Deutsch cases yourself.\n\n"
        "Top lane is constant: H -> H -> Splitter.\n"
        "Bottom lane is balanced: H -> Z -> H -> Splitter.\n\n"
        "The locked Splitters sort the deterministic answers:\n"
        "  |0> exits up to the constant sink\n"
        "  |1> exits down to the balanced sink."
    ),
    "hint": "Top: H-H. Bottom: H-Z-H. Splitters are already placed.",
    "pre_placed": {
        (0, 2): (GEN, RIGHT, None),
        (8, 2): (SPLIT, RIGHT, None),
        (8, 1): (SINK, DOWN, ZERO),
        (0, 4): (GEN, RIGHT, None),
        (8, 4): (SPLIT, RIGHT, None),
        (8, 5): (SINK, DOWN, ONE),
    },
    "locked": {(0, 2), (8, 2), (8, 1),
               (0, 4), (8, 4), (8, 5)},
    "available": [BELT, H, Z],
    "gate_limits": {H: 4, Z: 1},
    "win_count": 5,
    "camera": (4, 3),
}


# ---------------------------------------------------------------------------
# Chapter 12: Quantum Cloning
# ---------------------------------------------------------------------------

_CH12_CONCEPT = (
    "The No-Cloning Theorem says there is no universal machine\n"
    "that copies an arbitrary unknown quantum state.\n\n"
    "Known basis states are different. If you know the input is\n"
    "either |0> or |1>, CNOT can copy it onto a fresh |0> target:\n"
    "  |0>|0> -> |0>|0>\n"
    "  |1>|0> -> |1>|1>\n\n"
    "That does not clone superposition. With alpha|0> + beta|1>,\n"
    "CNOT creates entanglement, not two independent copies."
)

CH12_L1 = {
    "name": "Classical Copy",
    "description": "Use CNOT to copy a known |1> onto a fresh |0>.",
    "briefing": (
        "CNOT can copy classical basis states.\n\n"
        "The top lane is flipped to a known |1> by the locked X.\n"
        "The bottom lane stays a fresh |0> target.\n\n"
        "Place CNOT with the top lane as control and the bottom\n"
        "lane as target. Both exits should become |1>."
    ),
    "hint": "Place CNOT on the bottom lane under the top control lane.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (1, 2): (X, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (9, 2): (SINK, RIGHT, ONE),
        (9, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (1, 2), (-1, 3), (9, 2), (9, 3)},
    "available": [BELT, CNOT],
    "gate_limits": {CNOT: 1},
    "win_count": 5,
    "camera": (4, 3),
}

CH12_L2 = {
    "name": "Redundant Classical Channel",
    "description": "Copy a known bit with CNOT before the original hits noise.",
    "briefing": (
        "Use CNOT to make a backup of a known classical |1>.\n\n"
        "Top lane: original |1>, then locked Noise.\n"
        "Bottom lane: fresh |0> target, kept clean.\n\n"
        "CNOT copies the known basis state before the noisy part.\n"
        "The clean backup sink wants |1>."
    ),
    "hint": "CNOT before Noise. Top is control, bottom is target.",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (1, 3): (X, RIGHT, None),
        (7, 3): (NOISE, RIGHT, None),
        (-1, 4): (GEN, RIGHT, None),
        (9, 3): (SINK, RIGHT, None),
        (9, 4): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 3), (1, 3), (7, 3), (-1, 4), (9, 3), (9, 4)},
    "available": [BELT, CNOT],
    "gate_limits": {CNOT: 1},
    "win_count": 5,
    "camera": (4, 4),
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
        (0, 6): (GEN, RIGHT, None),
        (5, 4): (SWAP, RIGHT, None),
        (9, 3): (SINK, RIGHT, ZERO),
        (9, 4): (SINK, RIGHT, ONE),
        (9, 6): (SINK, RIGHT, PLUS),
    },
    "locked": {(0, 3), (0, 4), (0, 6), (5, 4), (9, 3), (9, 4), (9, 6)},
    "available": [BELT, H, X],
    "gate_limits": {X: 1, H: 1},
    "win_count": 5,
    "camera": (4, 4),
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
        "Place a single X gate to flip the top control to |1>.\n"
        "First CNOT flips middle to |1>.\n"
        "Middle feeds second CNOT's control.\n"
        "Second CNOT flips bottom to |1>.\n"
        "All three sinks want |1>.\n\n"
        "You only get one X gate — place it wisely."
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
    "gate_limits": {X: 1},
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
    "hint": "Build: H(locked) → Z(locked) → Noise(locked) → H → Splitter → |1> down to sink.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (2, 3): (H, RIGHT, None),
        (4, 3): (Z, RIGHT, None),
        (6, 3): (NOISE, RIGHT, None),
        (9, 5): (SINK, DOWN, ONE),
    },
    "locked": {(0, 3), (2, 3), (4, 3), (6, 3), (9, 5)},
    "available": [BELT, H, SPLIT],
    "gate_limits": {H: 1, SPLIT: 1},
    "win_count": 5,
    "camera": (5, 4),
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
        (9, 3): (SINK, RIGHT, ONE),
        (9, 4): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 3), (-1, 4), (2, 3), (5, 4), (9, 3), (9, 4)},
    "available": [BELT, H, X],
    "gate_limits": {H: 2, X: 1},
    "win_count": 5,
    "camera": (4, 4),
}


# ---------------------------------------------------------------------------
# Chapter 15: Algorithms
# ---------------------------------------------------------------------------

_CH15_CONCEPT = (
    "Quantum algorithms are built from the same small gates.\n\n"
    "QFT turns position into phase. Grover amplifies a marked\n"
    "answer. Teleportation moves an unknown state using shared\n"
    "entanglement plus correction. Shor uses period finding, with\n"
    "QFT as the readout step.\n\n"
    "No new magic gates here: these levels ask you to assemble\n"
    "the algorithm shapes from the gates you already know."
)

CH15_L1 = {
    "name": "QFT Ingredients",
    "description": "Build the Fourier-transform shape with H, CZ, and SWAP.",
    "briefing": (
        "QFT is built from smaller pieces:\n"
        "Hadamards create frequency-like superposition,\n"
        "controlled phase gates connect the lanes,\n"
        "and SWAP reverses output order.\n\n"
        "Build the two-lane QFT shape with H, CZ, and SWAP.\n"
        "Both outputs should stay superposed."
    ),
    "hint": "Use H on both lanes; CZ and SWAP are the QFT-shaped middle.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (9, 2): (SINK, RIGHT, PLUS),
        (9, 3): (SINK, RIGHT, PLUS),
    },
    "locked": {(-1, 2), (-1, 3), (9, 2), (9, 3)},
    "available": [BELT, H, CZ, SWAP],
    "gate_limits": {H: 2, CZ: 1, SWAP: 1},
    "win_count": 5,
    "camera": (4, 3),
}

CH15_L2 = {
    "name": "Grover Search",
    "description": "Prepare |++>, then amplify the marked |11> answer.",
    "briefing": (
        "Grover search starts with a uniform superposition.\n\n"
        "Build it from simple gates:\n"
        "  1. H on both lanes to make |++>\n"
        "  2. CZ as the oracle marking |11>\n"
        "  3. H, X, CZ, X, H as the diffusion step\n\n"
        "Both sinks want the amplified |1> result."
    ),
    "hint": "Recipe: H, CZ, H-X-CZ-X-H across both lanes.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (14, 2): (SINK, RIGHT, ONE),
        (14, 3): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 2), (-1, 3), (14, 2), (14, 3)},
    "available": [BELT, H, X, CZ],
    "gate_limits": {H: 6, X: 4, CZ: 2},
    "win_count": 5,
    "camera": (6, 3),
}

CH15_L3 = {
    "name": "Teleport Blueprint",
    "description": "Build the Bell-pair and Bell-measurement half of teleportation.",
    "briefing": (
        "Teleportation is not a single gate.\n"
        "It is a circuit: create an entangled Bell pair,\n"
        "mix the source with one half using CNOT and H,\n"
        "then measure the source lanes.\n\n"
        "This level builds that Bell-measurement half.\n"
        "Classical correction wiring comes later."
    ),
    "hint": "Use H and CNOTs, then route the top two lanes into measurements.",
    "win_type": "measure",
    "pre_placed": {
        (-1, 1): (GEN, RIGHT, None),
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (10, 1): (MEAS, RIGHT, None),
        (10, 2): (MEAS, RIGHT, None),
        (10, 3): (SINK, RIGHT, None),
    },
    "locked": {(-1, 1), (-1, 2), (-1, 3), (10, 1), (10, 2), (10, 3)},
    "available": [BELT, H, CNOT],
    "gate_limits": {H: 2, CNOT: 2},
    "win_count": 10,
    "camera": (4, 2),
}

CH15_L4 = {
    "name": "Shor Readout",
    "description": "Build a tiny period-finding readout from kickback and QFT ingredients.",
    "briefing": (
        "Shor's algorithm is too large to be one factory tile.\n"
        "The important game-sized idea is period readout:\n"
        "prepare superposition, use phase kickback, then measure.\n\n"
        "Build a small H -> CZ -> H-style readout circuit\n"
        "and send both lanes into measurement."
    ),
    "hint": "H for superposition, CZ for kickback, H again before measurement.",
    "win_type": "measure",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (9, 2): (MEAS, RIGHT, None),
        (9, 3): (MEAS, RIGHT, None),
    },
    "locked": {(-1, 2), (-1, 3), (9, 2), (9, 3)},
    "available": [BELT, H, CZ],
    "gate_limits": {H: 4, CZ: 1},
    "win_count": 10,
    "camera": (4, 3),
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
        "levels": [CH11_L2, CH11_L3],
    },
    {
        "name": "Quantum Cloning",
        "subtitle": "Classical copying and the no-cloning limit",
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
    {
        "name": "Algorithms",
        "subtitle": "QFT, Grover, teleportation, and toy Shor",
        "concept": _CH15_CONCEPT,
        "color": (120, 210, 255),
        "levels": [CH15_L1, CH15_L2, CH15_L3, CH15_L4],
    },
]

# Flat list for backwards compatibility (completion tracking uses global indices)
ALL_LEVELS = []
for _ch in CHAPTERS:
    ALL_LEVELS.extend(_ch["levels"])


def chapter_level_offset(ch_idx):
    return sum(len(CHAPTERS[i]["levels"]) for i in range(ch_idx))
