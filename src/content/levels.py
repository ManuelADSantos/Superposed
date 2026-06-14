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
MEAS = "measurement"
SPLIT = "splitter"


# ---------------------------------------------------------------------------
# Chapter 1: Classical Foundations
# ---------------------------------------------------------------------------

_CH1_CONCEPT = (
    "In computing, information is carried by signals — tiny pulses\n"
    "of energy traveling through circuits.\n\n"
    "In this factory, those signals are qubits. They travel\n"
    "along conveyor belts from generators to output sinks.\n\n"
    "Every qubit starts as |0⟩ (red). The X gate is the quantum\n"
    "NOT gate — it flips |0⟩ to |1⟩ and |1⟩ to |0⟩, just like\n"
    "a classical NOT."
)

CH1_L1 = {
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
    "description": "Flip |0⟩ into |1⟩ using the X gate.",
    "briefing": (
        "The X gate is the quantum NOT gate.\n"
        "It flips |0⟩ (red) into |1⟩ (blue) and vice versa.\n\n"
        "The sink wants blue |1⟩ qubits, but the generator\n"
        "only makes red |0⟩.  Use the X gate to flip them!"
    ),
    "hint": "Place an X gate on the path to flip |0⟩ → |1⟩",
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
        "Top sink wants |0⟩ — the generator already makes that,\n"
        "so just run a belt straight across.\n\n"
        "Bottom sink wants |1⟩ — you'll need to flip the qubit\n"
        "with an X gate somewhere along the path.\n\n"
        "Build both pipelines at the same time!"
    ),
    "hint": "Top: belt only → |0⟩.  Bottom: add X gate → |1⟩",
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
    "either |0⟩ or |1⟩ with equal probability — 50/50.\n"
    "The superposition is destroyed forever."
)

CH2_L1 = {
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
        "  Top lane:    deliver |0⟩ unchanged\n"
        "  Middle lane: flip |0⟩ into |1⟩\n"
        "  Bottom lane: put |0⟩ into superposition\n\n"
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
        "  Connect it with belts — it flips |0⟩ to |1⟩ for you.\n\n"
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
    "becoming |0⟩ or |1⟩. You can never predict which.\n"
    "This randomness is fundamental, not a limitation.\n\n"
    "The Splitter is a quantum router that measures and sorts:\n"
    "  |0⟩ qubits go straight\n"
    "  |1⟩ qubits turn clockwise\n\n"
    "Feed it superposition and you get a random 50/50 split\n"
    "into two separate paths."
)

CH3_L1 = {
    "name": "Collapse",
    "description": "Measure superposition and watch it collapse.",
    "briefing": (
        "Measurement collapses superposition!\n\n"
        "A purple (superposed) qubit becomes either red |0⟩\n"
        "or blue |1⟩ with equal probability — 50/50.\n"
        "You can never predict which.\n\n"
        "Route qubits through H → Measurement.\n"
        "The measurement gate absorbs the qubit and records\n"
        "the result in its histogram.\n\n"
        "Collapse 10 qubits to win."
    ),
    "hint": "H → Measure: watch the histogram fill up with random results",
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
        "  |0⟩ (red)  → exits straight ahead\n"
        "  |1⟩ (blue) → turns clockwise\n\n"
        "Feed superposed qubits into the Splitter to split\n"
        "the stream 50/50. Route each output to the\n"
        "matching sink: red to the |0⟩ sink, blue to the |1⟩ sink.\n\n"
        "Both sinks must collect 3 qubits to win."
    ),
    "hint": "H → Splitter sorts by state. Belt each output to its sink.",
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
    "The Z gate flips the phase: |+⟩ becomes |−⟩. These look\n"
    "identical (both purple), but behave differently.\n\n"
    "The key insight: H → Z → H always produces |1⟩.\n"
    "The Z phase flip causes destructive interference —\n"
    "the |0⟩ component cancels out.\n\n"
    "This is the foundation of every quantum algorithm:\n"
    "manipulate phase to make wrong answers cancel\n"
    "and right answers amplify."
)

CH4_L1 = {
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
        "Like X, it flips bits:  Y|0⟩ = |1⟩,  Y|1⟩ = |0⟩.\n"
        "Unlike X, it also flips the phase of superposition:\n"
        "  Y|+⟩ = |−⟩   and   Y|−⟩ = |+⟩\n\n"
        "The sink wants |1⟩ and the generator makes |0⟩.\n"
        "Route the qubit through Y to flip it.\n\n"
        "Note: Y alone looks like X here — the phase difference\n"
        "only shows up in interference.  That comes next."
    ),
    "hint": "Place a Y gate on the path — it flips |0⟩ to |1⟩",
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
    "description": "Two locked H gates — what do you place between them to get |1⟩?",
    "briefing": (
        "Two Hadamard gates are locked in place.\n"
        "Every qubit passes through both of them.\n\n"
        "H·H = identity → if nothing is between them, you get |0⟩ back.\n"
        "The sink wants |1⟩.  Just belts won't work.\n\n"
        "Experiment: what happens when Y sits between two H gates?\n"
        "  H|0⟩ = |+⟩,  Y|+⟩ = |−⟩,  H|−⟩ = |1⟩\n\n"
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
    "The CNOT gate is the first two-qubit gate you'll use.\n\n"
    "It has two inputs:\n"
    "  Control — enters from the top\n"
    "  Target  — enters from the left\n\n"
    "Rule: if the control is |1⟩, the target gets flipped.\n"
    "Simple enough — but something magical happens when\n"
    "the control is in superposition.\n\n"
    "The target doesn't flip or not-flip — it does BOTH.\n"
    "The two qubits become entangled: measuring one\n"
    "instantly determines the other. Einstein called this\n"
    "'spooky action at a distance.'"
)

CH5_L1 = {
    "name": "Controlled Flip",
    "description": "CNOT flips the target when the control is |1⟩.",
    "briefing": (
        "The CNOT gate has two inputs:\n"
        "  Control — enters from the top\n"
        "  Target  — enters from the left\n\n"
        "The rule: if control = |1⟩, target gets flipped.\n"
        "  |0⟩ → |1⟩  and  |1⟩ → |0⟩\n"
        "If control = |0⟩, nothing happens.\n\n"
        "Both generators make |0⟩.  Use X on the control\n"
        "path to flip it to |1⟩, then the CNOT will\n"
        "flip the target too.  Both sinks want |1⟩."
    ),
    "hint": "X on the control (top) path — CNOT flips the target",
    "pre_placed": {
        (4, -1): (GEN, DOWN, None),
        (-1, 2): (GEN, RIGHT, None),
        (4, 2): (CNOT, RIGHT, None),
        (8, 2): (SINK, RIGHT, ONE),
        (4, 6): (SINK, DOWN, ONE),
    },
    "locked": {(4, -1), (-1, 2), (4, 2), (8, 2), (4, 6)},
    "available": [BELT, X],
    "win_count": 5,
    "camera": (4, 2),
}

CH5_L2 = {
    "name": "Bell State",
    "description": "Superposition + CNOT creates entangled pairs.",
    "briefing": (
        "Now replace X with H on the control path.\n\n"
        "When the control is in superposition:\n"
        "  CNOT doesn't flip or not-flip — it does BOTH.\n"
        "  The two qubits become entangled.\n\n"
        "Entangled qubits share their fate:\n"
        "  if one collapses to |0⟩, the other does too.\n"
        "  if one collapses to |1⟩, so does the other.\n\n"
        "Watch for the golden ring — it marks entanglement.\n"
        "Place the CNOT yourself this time."
    ),
    "hint": "H on the control (top) path, CNOT at the crossing",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (5, -1): (GEN, DOWN, None),
        (10, 3): (SINK, RIGHT, None),
        (5, 8): (SINK, DOWN, None),
    },
    "locked": {(-1, 3), (5, -1), (10, 3), (5, 8)},
    "available": [BELT, H, CNOT],
    "win_count": 5,
    "camera": (5, 3),
}


# ---------------------------------------------------------------------------
# Chapter 6: Multi-Qubit Operations
# ---------------------------------------------------------------------------

_CH6_CONCEPT = (
    "Real quantum circuits use multiple qubits working together.\n\n"
    "The CZ gate applies a phase flip controlled by one qubit\n"
    "onto another. A key concept: PHASE KICKBACK.\n"
    "When a target qubit is |1⟩ and the control is in\n"
    "superposition, the phase gets 'kicked back' onto\n"
    "the control — a trick used in most quantum algorithms.\n\n"
    "The SWAP gate exchanges the states of two qubits entirely.\n"
    "After a SWAP, each qubit carries what the other had."
)

CH6_L1 = {
    "name": "Phase Kickback",
    "description": "A |1⟩ target kicks its phase back onto a superposition control.",
    "briefing": (
        "CZ is Controlled-Z: if the control qubit is |1⟩,\n"
        "it applies Z to the target.  But something stranger\n"
        "happens when the ROLES are reversed.\n\n"
        "If the TARGET is |1⟩ and the CONTROL is in superposition:\n"
        "  the control's own phase gets flipped — |+⟩ becomes |−⟩.\n"
        "This is called PHASE KICKBACK.\n\n"
        "Circuit to build:\n"
        "  Horizontal stream (target): X before CZ → |1⟩\n"
        "  Vertical stream (control):  H before CZ → |+⟩\n"
        "After CZ: control is |−⟩ — apply H to collapse it to |1⟩.\n"
        "Both sinks want |1⟩."
    ),
    "hint": "H on horizontal, X on vertical, CZ at crossing, H after CZ on vertical",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (5, -1): (GEN, DOWN, None),
        (10, 3): (SINK, RIGHT, ONE),
        (5, 9): (SINK, DOWN, ONE),
    },
    "locked": {(-1, 3), (5, -1), (10, 3), (5, 9)},
    "available": [BELT, H, X, CZ],
    "win_count": 5,
    "camera": (5, 4),
}

CH6_L2 = {
    "name": "Stream Crossing",
    "description": "SWAP exchanges the states of two qubit streams.",
    "briefing": (
        "The SWAP gate exchanges the quantum states of two qubits.\n"
        "After a SWAP, each qubit carries the other's original state.\n\n"
        "Two streams cross at a SWAP gate:\n"
        "  Horizontal stream: |0⟩ (straight from the generator)\n"
        "  Vertical stream:   |1⟩ (flip it with X first)\n\n"
        "After the SWAP:\n"
        "  Horizontal exit carries the vertical stream's state → |1⟩\n"
        "  Vertical exit carries the horizontal stream's state → |0⟩\n\n"
        "Route each exit to the matching sink."
    ),
    "hint": "X on the vertical path, SWAP at the crossing, belt the exits to sinks",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (5, -1): (GEN, DOWN, None),
        (10, 3): (SINK, RIGHT, ONE),
        (5, 9): (SINK, DOWN, ZERO),
    },
    "locked": {(-1, 3), (5, -1), (10, 3), (5, 9)},
    "available": [BELT, X, SWAP],
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
]

COMING_SOON = [
    {"name": "Interference Patterns", "subtitle": "S, T, and phase gates"},
    {"name": "Quantum Teleportation", "subtitle": "Sending state without sending qubits"},
    {"name": "Deutsch-Jozsa", "subtitle": "The first quantum speedup"},
    {"name": "Grover's Search", "subtitle": "Finding needles in haystacks"},
    {"name": "Quantum Fourier Transform", "subtitle": "Frequency analysis with qubits"},
    {"name": "Shor's Algorithm", "subtitle": "Breaking encryption with quantum"},
    {"name": "Quantum Noise", "subtitle": "Decoherence and imperfections"},
    {"name": "Error Correction", "subtitle": "Protecting quantum information"},
]

# Flat list for backwards compatibility (completion tracking uses global indices)
ALL_LEVELS = []
for _ch in CHAPTERS:
    ALL_LEVELS.extend(_ch["levels"])


def chapter_level_offset(ch_idx):
    return sum(len(CHAPTERS[i]["levels"]) for i in range(ch_idx))
