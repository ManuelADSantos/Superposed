"""Unit tests for all gate transforms, entanglement, and edge cases."""

from __future__ import annotations

import unittest
import random

import pygame  # noqa: E402 — needed by sprite functions at registration time

from src.engine.gate_registry import load_gates
load_gates()

from src.core.entities import QubitState, QubitItem, Direction, Tile
from src.core.world import (
    reset_world,
    create_entangle_group, register_entangled,
    get_entangled_partners, break_entanglement,
)
from src.engine.gates.hadamard import _transform as hadamard
from src.engine.gates.x_gate import _transform as x_gate
from src.engine.gates.z_gate import _transform as z_gate
from src.engine.gates.cnot import _transform as cnot
from src.engine.gates.measurement import _transform as measure
from src.engine.gates.splitter import _transform as splitter


# ── Helpers ────────────────────────────────────────────────────────────────

def _qubit(state=QubitState.ZERO, phase=False):
    q = QubitItem(state)
    q.phase_flipped = phase
    return q


def _tile(**kw):
    t = Tile()
    for k, v in kw.items():
        setattr(t, k, v)
    return t


# ══════════════════════════════════════════════════════════════════════════
# X gate
# ══════════════════════════════════════════════════════════════════════════

class TestXGate(unittest.TestCase):

    def test_zero_to_one(self):
        q = _qubit(QubitState.ZERO)
        x_gate(q)
        self.assertEqual(q.state, QubitState.ONE)

    def test_one_to_zero(self):
        q = _qubit(QubitState.ONE)
        x_gate(q)
        self.assertEqual(q.state, QubitState.ZERO)

    def test_superposition_unchanged(self):
        q = _qubit(QubitState.SUPERPOSITION)
        x_gate(q)
        self.assertEqual(q.state, QubitState.SUPERPOSITION)

    def test_double_x_is_identity(self):
        q = _qubit(QubitState.ZERO)
        x_gate(q)
        x_gate(q)
        self.assertEqual(q.state, QubitState.ZERO)


# ══════════════════════════════════════════════════════════════════════════
# Hadamard gate
# ══════════════════════════════════════════════════════════════════════════

class TestHadamard(unittest.TestCase):

    def test_zero_to_superposition(self):
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        self.assertEqual(q.state, QubitState.SUPERPOSITION)
        self.assertFalse(q.phase_flipped)

    def test_one_to_superposition_with_phase(self):
        q = _qubit(QubitState.ONE)
        hadamard(q)
        self.assertEqual(q.state, QubitState.SUPERPOSITION)
        self.assertTrue(q.phase_flipped)

    def test_superposition_no_phase_to_zero(self):
        q = _qubit(QubitState.SUPERPOSITION, phase=False)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ZERO)
        self.assertFalse(q.phase_flipped)

    def test_superposition_with_phase_to_one(self):
        q = _qubit(QubitState.SUPERPOSITION, phase=True)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ONE)
        self.assertFalse(q.phase_flipped)

    def test_double_h_is_identity(self):
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ZERO)

    def test_h_on_one_double_is_identity(self):
        q = _qubit(QubitState.ONE)
        hadamard(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ONE)


# ══════════════════════════════════════════════════════════════════════════
# Z gate
# ══════════════════════════════════════════════════════════════════════════

class TestZGate(unittest.TestCase):

    def test_z_on_zero_no_effect(self):
        q = _qubit(QubitState.ZERO)
        z_gate(q)
        self.assertEqual(q.state, QubitState.ZERO)
        self.assertFalse(q.phase_flipped)

    def test_z_on_one_no_effect(self):
        q = _qubit(QubitState.ONE)
        z_gate(q)
        self.assertEqual(q.state, QubitState.ONE)

    def test_z_on_superposition_flips_phase(self):
        q = _qubit(QubitState.SUPERPOSITION, phase=False)
        z_gate(q)
        self.assertTrue(q.phase_flipped)

    def test_z_on_superposition_double_is_identity(self):
        q = _qubit(QubitState.SUPERPOSITION, phase=False)
        z_gate(q)
        z_gate(q)
        self.assertFalse(q.phase_flipped)


# ══════════════════════════════════════════════════════════════════════════
# Interference: H → Z → H = deterministic |1⟩
# ══════════════════════════════════════════════════════════════════════════

class TestInterference(unittest.TestCase):

    def test_hzh_gives_one(self):
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        z_gate(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ONE)
        self.assertFalse(q.phase_flipped)

    def test_hh_gives_zero(self):
        """H→H with no Z in between should return to |0⟩."""
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ZERO)


# ══════════════════════════════════════════════════════════════════════════
# CNOT gate
# ══════════════════════════════════════════════════════════════════════════

class TestCNOT(unittest.TestCase):

    def setUp(self):
        reset_world()

    def test_control_zero_no_flip(self):
        c = _qubit(QubitState.ZERO)
        t = _qubit(QubitState.ZERO)
        cnot(c, t)
        self.assertEqual(t.state, QubitState.ZERO)

    def test_control_one_flips_target(self):
        c = _qubit(QubitState.ONE)
        t = _qubit(QubitState.ZERO)
        cnot(c, t)
        self.assertEqual(t.state, QubitState.ONE)

    def test_control_one_flips_one_to_zero(self):
        c = _qubit(QubitState.ONE)
        t = _qubit(QubitState.ONE)
        cnot(c, t)
        self.assertEqual(t.state, QubitState.ZERO)

    def test_control_superposition_entangles(self):
        c = _qubit(QubitState.SUPERPOSITION)
        t = _qubit(QubitState.ZERO)
        cnot(c, t)
        self.assertEqual(t.state, QubitState.SUPERPOSITION)
        self.assertIsNotNone(c.entangle_group)
        self.assertEqual(c.entangle_group, t.entangle_group)

    def test_control_superposition_target_already_one(self):
        """Superposed control + |1⟩ target — target becomes superposition and entangled."""
        c = _qubit(QubitState.SUPERPOSITION)
        t = _qubit(QubitState.ONE)
        cnot(c, t)
        # CNOT puts any basis-state target into superposition when control is superposed
        self.assertEqual(t.state, QubitState.SUPERPOSITION)
        self.assertIsNotNone(t.entangle_group)

    def test_entangled_partners_found(self):
        c = _qubit(QubitState.SUPERPOSITION)
        t = _qubit(QubitState.ZERO)
        cnot(c, t)
        partners = get_entangled_partners(c)
        self.assertEqual(len(partners), 1)
        self.assertEqual(partners[0].uid, t.uid)


# ══════════════════════════════════════════════════════════════════════════
# Measurement
# ══════════════════════════════════════════════════════════════════════════

class TestMeasurement(unittest.TestCase):

    def setUp(self):
        reset_world()

    def test_measure_zero_stays_zero(self):
        q = _qubit(QubitState.ZERO)
        tile = _tile()
        measure(q, tile)
        self.assertEqual(q.state, QubitState.ZERO)
        self.assertEqual(tile.measurements, [QubitState.ZERO])

    def test_measure_one_stays_one(self):
        q = _qubit(QubitState.ONE)
        tile = _tile()
        measure(q, tile)
        self.assertEqual(q.state, QubitState.ONE)

    def test_measure_superposition_collapses(self):
        q = _qubit(QubitState.SUPERPOSITION)
        tile = _tile()
        measure(q, tile)
        self.assertIn(q.state, (QubitState.ZERO, QubitState.ONE))
        self.assertFalse(q.phase_flipped)

    def test_measure_superposition_distribution(self):
        """Over many trials, measurement should be roughly 50/50."""
        random.seed(42)
        zeros = 0
        for _ in range(200):
            q = _qubit(QubitState.SUPERPOSITION)
            tile = _tile()
            measure(q, tile)
            if q.state == QubitState.ZERO:
                zeros += 1
        # With 200 trials, expect 60-140 zeros (very loose bounds)
        self.assertGreater(zeros, 50)
        self.assertLess(zeros, 150)

    def test_measure_collapses_entangled_partner(self):
        c = _qubit(QubitState.SUPERPOSITION)
        t = _qubit(QubitState.ZERO)
        cnot(c, t)  # entangles them
        tile = _tile()
        measure(c, tile)
        # Both should have collapsed to the same state
        self.assertEqual(c.state, t.state)
        self.assertIn(c.state, (QubitState.ZERO, QubitState.ONE))

    def test_histogram_caps_at_20(self):
        tile = _tile()
        for _ in range(25):
            q = _qubit(QubitState.ZERO)
            measure(q, tile)
        self.assertEqual(len(tile.measurements), 20)

    def test_measure_flash_set(self):
        q = _qubit(QubitState.ZERO)
        tile = _tile()
        measure(q, tile)
        self.assertAlmostEqual(tile.measure_flash, 0.35)


# ══════════════════════════════════════════════════════════════════════════
# Splitter
# ══════════════════════════════════════════════════════════════════════════

class TestSplitter(unittest.TestCase):

    def setUp(self):
        reset_world()

    def _run_splitter(self, state, direction=Direction.RIGHT):
        q = _qubit(state)
        tile = _tile(direction=direction)
        ejected = []
        def eject(sx, sy, nx, ny, item):
            ejected.append((nx - sx, ny - sy, item))
        splitter(0, 0, tile, q, eject)
        return q, ejected

    def test_zero_goes_straight(self):
        q, ejected = self._run_splitter(QubitState.ZERO)
        self.assertEqual(len(ejected), 1)
        self.assertEqual(ejected[0][:2], (1, 0))  # RIGHT = (1, 0)

    def test_one_goes_cw(self):
        q, ejected = self._run_splitter(QubitState.ONE)
        self.assertEqual(len(ejected), 1)
        self.assertEqual(ejected[0][:2], (0, 1))  # CW of RIGHT = DOWN = (0, 1)

    def test_superposition_collapses(self):
        q, ejected = self._run_splitter(QubitState.SUPERPOSITION)
        self.assertIn(q.state, (QubitState.ZERO, QubitState.ONE))
        self.assertEqual(len(ejected), 1)

    def test_superposition_distribution(self):
        """Over many trials, splitter should route roughly 50/50."""
        random.seed(42)
        straight = 0
        for _ in range(200):
            _, ejected = self._run_splitter(QubitState.SUPERPOSITION)
            if ejected[0][:2] == (1, 0):
                straight += 1
        self.assertGreater(straight, 50)
        self.assertLess(straight, 150)

    def test_direction_down_routes_correctly(self):
        """When gate faces DOWN, |0⟩ goes (0,1) and |1⟩ goes (-1,0)."""
        _, ej_zero = self._run_splitter(QubitState.ZERO, Direction.DOWN)
        self.assertEqual(ej_zero[0][:2], (0, 1))
        _, ej_one = self._run_splitter(QubitState.ONE, Direction.DOWN)
        self.assertEqual(ej_one[0][:2], (-1, 0))


# ══════════════════════════════════════════════════════════════════════════
# Entanglement registry
# ══════════════════════════════════════════════════════════════════════════

class TestEntanglement(unittest.TestCase):

    def setUp(self):
        reset_world()

    def test_break_entanglement(self):
        q1 = _qubit(QubitState.SUPERPOSITION)
        q2 = _qubit(QubitState.SUPERPOSITION)
        gid = create_entangle_group()
        register_entangled(gid, q1)
        register_entangled(gid, q2)
        self.assertEqual(len(get_entangled_partners(q1)), 1)
        break_entanglement(q1)
        self.assertIsNone(q1.entangle_group)
        self.assertEqual(len(get_entangled_partners(q1)), 0)

    def test_hadamard_breaks_entanglement(self):
        """H on a superposed qubit collapses it, which should break entanglement."""
        q1 = _qubit(QubitState.SUPERPOSITION)
        q2 = _qubit(QubitState.SUPERPOSITION)
        gid = create_entangle_group()
        register_entangled(gid, q1)
        register_entangled(gid, q2)
        hadamard(q1)  # H|+⟩ = |0⟩, breaks entanglement
        self.assertIsNone(q1.entangle_group)


# ══════════════════════════════════════════════════════════════════════════
# Safe transform (error handling in simulation)
# ══════════════════════════════════════════════════════════════════════════

class TestSafeTransform(unittest.TestCase):

    def test_broken_transform_does_not_crash(self):
        from src.engine.simulation import _safe_transform
        from src.engine.gate_registry import GateDef, Category

        def bad_transform(item):
            raise ValueError("intentional test error")

        gate = GateDef(
            id="test_broken", name="Broken", tip="test",
            color=(255, 0, 0), category=Category.SINGLE,
            transform=bad_transform,
        )
        q = _qubit(QubitState.ZERO)
        # Should print to stderr but not raise
        _safe_transform(gate, q)
        # Qubit should be unmodified
        self.assertEqual(q.state, QubitState.ZERO)


if __name__ == "__main__":
    unittest.main()
