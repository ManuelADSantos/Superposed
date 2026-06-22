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
        (4, 2): (MEAS, RIGHT, None),
        (2, 2): (H, RIGHT, None),
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
        "  |0⟩ (red)  → exits straight ahead\n"
        "  |1⟩ (blue) → turns clockwise\n\n"
        "Feed superposed qubits into the Splitter to split\n"
        "the stream 50/50. Route each output to the\n"
        "matching sink: red to the |0⟩ sink, blue to the |1⟩ sink.\n\n"
        "Both sinks must collect 10 qubits to win."
    ),
    "hint": "H → Splitter sorts by state. Belt each output to its sink.",
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
    "The Z gate flips the phase: |+⟩ becomes |−⟩. These look\n"
    "identical (both purple), but behave differently.\n\n"
    "The key insight: H → Z → H always produces |1⟩.\n"
    "The phase flip causes destructive interference —\n"
    "the |0⟩ component cancels out. This is the foundation\n"
    "of every quantum algorithm."
)

CH4_L1 = {
    "name": "Interference",
    "description": "Discover how H → Z → H always produces |1⟩.",
    "briefing": (
        "The Z gate flips the phase of a qubit.\n"
        "Watch the tick on the qubit ring — Z rotates it 180°.\n\n"
        "Route qubits through  H → Z → H.\n"
        "H creates |+⟩, Z flips its phase to |−⟩.\n"
        "The second H converts that phase difference into\n"
        "a bit flip: |−⟩ always becomes |1⟩, never random.\n\n"
        "This is interference — the phase is consumed\n"
        "by the second H to produce a deterministic output.\n\n"
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
        "Like X, it flips bits. Unlike X, it also flips\n"
        "the phase of a superposition:\n"
        "  Y|+⟩ = |−⟩   and   Y|−⟩ = |+⟩\n\n"
        "A locked H gate puts the qubit into |+⟩.\n"
        "The sink wants |−⟩ — a superposition with the phase\n"
        "tick pointing up (180°).\n"
        "Place Y after H to flip the phase."
    ),
    "hint": "H makes |+⟩, Y flips it to |−⟩ — match the phase tick.",
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
    "The CNOT gate is the first two-qubit gate you'll use.\n"
    "It spans two cells — like a real quantum circuit.\n\n"
    "Two parallel qubit streams flow through it:\n"
    "  Top  = Control (marked with a dot)\n"
    "  Bottom = Target (the gate symbol)\n\n"
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
        "The CNOT gate spans two cells:\n"
        "  Top row  = Control (dot)\n"
        "  Bottom row = Target (gate)\n\n"
        "Both streams flow left to right.\n"
        "The rule: if control = |1⟩, target gets flipped.\n"
        "  |0⟩ → |1⟩  and  |1⟩ → |0⟩\n"
        "If control = |0⟩, nothing happens.\n\n"
        "Both generators make |0⟩.  Use X on the control\n"
        "path (top) to flip it to |1⟩, then the CNOT will\n"
        "flip the target too.  Both sinks want |1⟩."
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
        "Two parallel streams, both flowing left to right:\n"
        "  Control (top): H before CZ → |+⟩\n"
        "  Target (bottom): X before CZ → |1⟩\n"
        "After CZ: control is |−⟩ — apply H to collapse it to |1⟩.\n"
        "Both sinks want |1⟩."
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
        "  Top stream:    |1⟩ (straight from the generator)\n"
        "  Bottom stream: |0⟩ (straight from the generator)\n\n"
        "After the SWAP:\n"
        "  Top exit carries the bottom stream's state → |0⟩\n"
        "  Bottom exit carries the top stream's state → |1⟩\n\n"
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
    "unlocked": {(1, 2), (2, 2), (0, 3), (1, 3), (2, 3)},
    "available": [BELT, SWAP],
    "gate_limits": {SWAP: 1},
    "win_count": 10,
    "camera": (2, 3),
}


# ---------------------------------------------------------------------------
# Chapter 7: Quantum Circuits
# ---------------------------------------------------------------------------

_CH7_CONCEPT = (
    "Entanglement doesn't stop at two qubits.\n\n"
    "By chaining CNOT gates, you can propagate entanglement\n"
    "across many qubit streams. When one partner is measured,\n"
    "ALL entangled partners collapse together.\n\n"
    "This is how real quantum circuits scale: small two-qubit\n"
    "interactions build up into large correlated systems.\n"
    "The key constraint is resources — you often have fewer\n"
    "gates than qubits, forcing creative circuit design."
)

CH7_L2 = {
    "name": "Entanglement Chain",
    "description": "Chain entanglement across three qubits with two CNOTs.",
    "briefing": (
        "Three parallel streams, three sinks — all want |1⟩.\n"
        "You only have ONE Hadamard gate.\n\n"
        "H alone converts one stream, but the others stay |0⟩.\n"
        "Use CNOT to chain entanglement across all three:\n"
        "  when the H-qubit collapses to |1⟩,\n"
        "  all entangled partners become |1⟩ too.\n\n"
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
# Chapter 8: Quantum Noise
# ---------------------------------------------------------------------------

_CH8_CONCEPT = (
    "Real quantum computers suffer from noise — random errors\n"
    "that corrupt qubits unpredictably.\n\n"
    "The Noise gate simulates this chaos: each qubit passing\n"
    "through is randomized to any of the six possible states\n"
    "AND sent out from a random direction.\n\n"
    "Your first defense: avoid the noise entirely.\n"
    "Route your qubits around noisy channels whenever possible."
)

CH8_L1 = {
    "name": "Noisy Channel",
    "description": "The direct path is corrupted — find a way around.",
    "briefing": (
        "A Noise gate sits on the direct path from\n"
        "generator to sink. Every qubit passing through\n"
        "gets randomized AND scattered in a random direction.\n\n"
        "The sink wants |0⟩ but noise randomizes\n"
        "both the state and the exit direction.\n\n"
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

CH8_L2 = {
    "name": "Noise Breaks Everything",
    "description": "Noise destroys interference — see the damage firsthand.",
    "briefing": (
        "Two assembly lines, both with H gates for interference.\n\n"
        "Top line: clean. H → Z → H produces |1⟩ reliably.\n"
        "Bottom line: a locked Noise gate sits between\n"
        "the Z and the second H. Noise randomizes the state,\n"
        "breaking the interference pattern.\n\n"
        "Both sinks want |1⟩.\n"
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

CH8_L3 = {
    "name": "Detour & Transform",
    "description": "Route around noise AND apply the right gates.",
    "briefing": (
        "Two lanes, two sinks, noise blocking the direct paths.\n\n"
        "Top sink wants |1⟩. Bottom sink wants |+⟩.\n"
        "Noise gates sit on both straight-line routes.\n\n"
        "Route around each noise gate, then apply the\n"
        "right transformation: X for |1⟩, H for |+⟩.\n\n"
        "This is the real challenge of noisy hardware:\n"
        "avoiding errors while still computing."
    ),
    "hint": "Detour both lanes around noise. Top: add X. Bottom: add H.",
    "pre_placed": {
        (0, 1): (GEN, RIGHT, None),
        (4, 1): (NOISE, RIGHT, None),
        (9, 1): (SINK, RIGHT, ONE),
        (0, 5): (GEN, RIGHT, None),
        (4, 5): (NOISE, RIGHT, None),
        (9, 5): (SINK, RIGHT, PLUS),
    },
    "locked": {(0, 1), (4, 1), (9, 1), (0, 5), (4, 5), (9, 5)},
    "available": [BELT, X, H],
    "gate_limits": {X: 1, H: 1},
    "win_count": 5,
    "camera": (4, 3),
}


# ---------------------------------------------------------------------------
# Chapter 9: Noise Management
# ---------------------------------------------------------------------------

_CH9_CONCEPT = (
    "You can't always avoid noise. But you CAN work with the chaos.\n\n"
    "Noise scatters qubits in random directions and randomizes\n"
    "their state. When noise is unavoidable, you need strategies:\n"
    "  1. Catch scattered qubits by covering all exits\n"
    "  2. Sort the random outputs with Splitters\n\n"
    "These techniques form the basis of error management\n"
    "in real quantum computing."
)

CH9_L1 = {
    "name": "Scatter Catch",
    "description": "Noise scatters qubits in all directions — catch them all.",
    "briefing": (
        "The Noise gate randomizes each qubit's state AND\n"
        "sends it out from a random direction.\n\n"
        "A qubit enters from the left, but it could exit\n"
        "up, right, or down — never back where it came from.\n\n"
        "Place sinks on all three possible exits to catch\n"
        "every qubit regardless of direction.\n"
        "The sinks accept any state."
    ),
    "hint": "Place sinks (or belts to sinks) on all 3 exit sides of the noise gate.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (4, 3): (NOISE, RIGHT, None),
    },
    "locked": {(0, 3), (4, 3)},
    "available": [BELT, SINK],
    "win_count": 10,
    "camera": (4, 3),
}

CH9_L2 = {
    "name": "Noisy Filter",
    "description": "Sort scattered noise output to collect useful qubits.",
    "briefing": (
        "Route qubits through a locked Noise gate.\n"
        "Noise randomizes their state, but some come out\n"
        "as |0⟩ or |1⟩ — the Splitter can sort those.\n\n"
        "Place Splitters after the noise exits to separate\n"
        "|0⟩ from |1⟩. Route |0⟩ qubits to the |0⟩ sink.\n\n"
        "Superposed noise outputs collapse randomly at the\n"
        "Splitter — some will still reach the sink."
    ),
    "hint": "Cover noise exits → Splitter on each path → route |0⟩ up to sink.",
    "pre_placed": {
        (0, 3): (GEN, RIGHT, None),
        (3, 3): (NOISE, RIGHT, None),
        (9, 0): (SINK, RIGHT, ZERO),
    },
    "locked": {(0, 3), (3, 3), (9, 0)},
    "available": [BELT, SPLIT],
    "win_count": 5,
    "camera": (5, 3),
}


# ---------------------------------------------------------------------------
# Chapter 10: Quantum Cloning
# ---------------------------------------------------------------------------

_CH10_CONCEPT = (
    "The No-Cloning Theorem says there is no universal machine\n"
    "that copies an arbitrary unknown quantum state.\n\n"
    "Known basis states are different. If you know the input is\n"
    "either |0⟩ or |1⟩, CNOT can copy it onto a fresh |0⟩ target:\n"
    "  |0⟩|0⟩ → |0⟩|0⟩\n"
    "  |1⟩|0⟩ → |1⟩|1⟩\n\n"
    "That does not clone superposition. With alpha|0⟩ + beta|1⟩,\n"
    "CNOT creates entanglement, not two independent copies.\n"
    "This is a fundamental limit of quantum mechanics."
)

CH10_L2 = {
    "name": "Backup Before Noise",
    "description": "Copy a known bit with CNOT before the original hits noise.",
    "briefing": (
        "Use CNOT to make a backup of a known classical |1⟩\n"
        "BEFORE the original passes through noise.\n\n"
        "Top lane: original |1⟩, then locked Noise gate.\n"
        "  The noise randomizes and scatters the original.\n"
        "Bottom lane: fresh |0⟩ target, kept clean.\n\n"
        "CNOT copies the |1⟩ before noise destroys it.\n"
        "The clean backup sink wants |1⟩.\n"
        "The original is lost to noise — that's expected."
    ),
    "hint": "CNOT before Noise. Top is control, bottom is target.",
    "pre_placed": {
        (-1, 3): (GEN, RIGHT, None),
        (1, 3): (X, RIGHT, None),
        (7, 3): (NOISE, RIGHT, None),
        (-1, 4): (GEN, RIGHT, None),
        (9, 4): (SINK, RIGHT, ONE),
    },
    "locked": {(-1, 3), (1, 3), (7, 3), (-1, 4), (9, 4)},
    "available": [BELT, CNOT],
    "gate_limits": {CNOT: 1},
    "win_count": 5,
    "camera": (4, 4),
}


# ---------------------------------------------------------------------------
# Chapter 11: Algorithms
# ---------------------------------------------------------------------------

_CH12_CONCEPT = (
    "Quantum algorithms are built from the same small gates.\n\n"
    "Deutsch's algorithm is the simplest: it distinguishes\n"
    "constant from balanced functions using interference.\n"
    "Grover amplifies a marked answer from a uniform mix.\n"
    "QFT turns position into phase.\n"
    "Teleportation moves an unknown state using entanglement.\n\n"
    "No new magic gates here: these levels ask you to assemble\n"
    "the algorithm shapes from the gates you already know."
)

CH12_L1 = {
    "name": "Deutsch Classifier",
    "description": "Build constant and balanced paths, then route the answers.",
    "briefing": (
        "Deutsch's algorithm distinguishes two types of functions:\n"
        "  CONSTANT leaves interference constructive → |0⟩\n"
        "  BALANCED makes interference destructive → |1⟩\n\n"
        "Top lane is constant: H → (nothing) → H.\n"
        "  Constructive interference produces |0⟩.\n"
        "Bottom lane is balanced: H → Z → H.\n"
        "  Destructive interference produces |1⟩.\n\n"
        "The locked Splitters sort the deterministic answers:\n"
        "  |0⟩ exits up to the constant sink\n"
        "  |1⟩ exits down to the balanced sink."
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

CH12_L2 = {
    "name": "QFT Shape",
    "description": "Assemble the Quantum Fourier Transform from locked components.",
    "briefing": (
        "QFT is built from smaller pieces:\n"
        "Hadamards create frequency-like superposition,\n"
        "controlled phase gates connect the lanes,\n"
        "and SWAP reverses output order.\n\n"
        "The circuit structure is locked in place:\n"
        "  H gates, CZ gate, and SWAP gate.\n"
        "Connect them with belts to complete the QFT."
    ),
    "hint": "Belt the locked gates together in sequence.",
    "pre_placed": {
        (-1, 2): (GEN, RIGHT, None),
        (-1, 3): (GEN, RIGHT, None),
        (1, 2): (H, RIGHT, None),
        (3, 3): (H, RIGHT, None),
        (5, 3): (CZ, RIGHT, None),
        (7, 3): (SWAP, RIGHT, None),
        (10, 2): (SINK, RIGHT, PLUS),
        (10, 3): (SINK, RIGHT, PLUS),
    },
    "locked": {(-1, 2), (-1, 3), (1, 2), (3, 3), (5, 3), (7, 3),
               (10, 2), (10, 3)},
    "available": [BELT],
    "win_count": 5,
    "camera": (4, 3),
}

CH12_L3 = {
    "name": "Grover Search",
    "description": "Prepare |++⟩, then amplify the marked |11⟩ answer.",
    "briefing": (
        "Grover search starts with a uniform superposition.\n\n"
        "Build it from simple gates:\n"
        "  1. H on both lanes to make |++⟩\n"
        "  2. CZ as the oracle marking |11⟩\n"
        "  3. H, X, CZ, X, H as the diffusion step\n\n"
        "Both sinks want the amplified |1⟩ result."
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

CH12_L4 = {
    "name": "Teleport Blueprint",
    "description": "Build the Bell-pair and Bell-measurement half of teleportation.",
    "briefing": (
        "Teleportation is not a single gate.\n"
        "It is a circuit: create an entangled Bell pair,\n"
        "mix the source with one half using CNOT and H,\n"
        "then measure the source lanes.\n\n"
        "Three lanes:\n"
        "  Top: the source qubit\n"
        "  Middle: one half of the Bell pair\n"
        "  Bottom: the other half → travels to the sink\n\n"
        "Build the Bell pair (H + CNOT on middle/bottom),\n"
        "then entangle the source with its half (CNOT + H),\n"
        "and measure the top two."
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
        "name": "Quantum Circuits",
        "subtitle": "Scaling entanglement across qubits",
        "concept": _CH7_CONCEPT,
        "color": (180, 255, 180),
        "levels": [CH7_L2],
    },
    {
        "name": "Quantum Noise",
        "subtitle": "Random errors and how to avoid them",
        "concept": _CH8_CONCEPT,
        "color": (200, 70, 70),
        "levels": [CH8_L1, CH8_L2, CH8_L3],
    },
    {
        "name": "Noise Management",
        "subtitle": "Working with chaos when you can't avoid it",
        "concept": _CH9_CONCEPT,
        "color": (255, 180, 100),
        "levels": [CH9_L1, CH9_L2],
    },
    {
        "name": "Quantum Cloning",
        "subtitle": "Classical copying and the no-cloning limit",
        "concept": _CH10_CONCEPT,
        "color": (100, 200, 140),
        "levels": [CH10_L2],
    },
    {
        "name": "Algorithms",
        "subtitle": "Deutsch, QFT, Grover, and teleportation",
        "concept": _CH12_CONCEPT,
        "color": (120, 210, 255),
        "levels": [CH12_L1, CH12_L2, CH12_L3, CH12_L4],
    },
]

# Flat list for backwards compatibility (completion tracking uses global indices)
ALL_LEVELS = []
for _ch in CHAPTERS:
    ALL_LEVELS.extend(_ch["levels"])


def chapter_level_offset(ch_idx):
    return sum(len(CHAPTERS[i]["levels"]) for i in range(ch_idx))
