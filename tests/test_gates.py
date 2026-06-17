"""Unit tests for all gate transforms, entanglement, and edge cases."""

from __future__ import annotations

import unittest
import random
import os
import math

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
from src.engine.gates.toffoli import _transform as toffoli
from src.engine.gates.qft import _transform as qft
from src.engine.gates.grover import _transform as grover
from src.engine.gates.shor import _transform as shor
from src.engine.gates.teleport import _transform as teleport
from src.engine.gates.measurement import _transform as measure
from src.engine.gates.splitter import _transform as splitter


def _qubit(state=QubitState.ZERO, phase=False):
    q = QubitItem(state)
    if phase:
        q.beta = -q.beta
    return q


def _tile(**kw):
    t = Tile()
    for k, v in kw.items():
        setattr(t, k, v)
    return t


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


# Hadamard gate

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

    def test_arbitrary_phase_angle(self):
        q = _qubit(QubitState.SUPERPOSITION)
        q.beta *= 1j
        self.assertAlmostEqual(q.phase_angle, math.pi / 2)
        self.assertAlmostEqual(q.bloch[1], 1.0)

    def test_basis_state_sprite_draws_phase_arrow(self):
        from src.ui import sprites

        calls = []
        draw_arrow = sprites._draw_phase_arrow

        def spy(*args):
            calls.append(args)

        try:
            sprites.clear_sprite_caches()
            sprites._draw_phase_arrow = spy
            sprites.get_qubit_sprite(QubitState.ZERO, 32, phase_angle=0.0, bloch=(0, 0, 1))
        finally:
            sprites._draw_phase_arrow = draw_arrow
            sprites.clear_sprite_caches()

        self.assertEqual(len(calls), 1)


# Z gate

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


# Interference: H → Z → H = deterministic |1>

class TestInterference(unittest.TestCase):

    def test_hzh_gives_one(self):
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        z_gate(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ONE)
        self.assertFalse(q.phase_flipped)

    def test_hh_gives_zero(self):
        """H→H with no Z in between should return to |0>."""
        q = _qubit(QubitState.ZERO)
        hadamard(q)
        hadamard(q)
        self.assertEqual(q.state, QubitState.ZERO)


# CNOT gate

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
        """Superposed control + |1> target — target becomes superposition and entangled."""
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

    def test_entangled_pair_can_merge_with_third_qubit(self):
        q1 = _qubit(QubitState.SUPERPOSITION)
        q2 = _qubit(QubitState.ZERO)
        q3 = _qubit(QubitState.ZERO)
        cnot(q1, q2)
        cnot(q2, q3)
        self.assertEqual(q1.entangle_group, q2.entangle_group)
        self.assertEqual(q1.entangle_group, q3.entangle_group)
        self.assertEqual(q3.state, QubitState.SUPERPOSITION)
        self.assertEqual({p.uid for p in get_entangled_partners(q1)}, {q2.uid, q3.uid})


class TestToffoli(unittest.TestCase):

    def setUp(self):
        reset_world()

    def test_two_controls_flip_target(self):
        c1 = _qubit(QubitState.ONE)
        c2 = _qubit(QubitState.ONE)
        t = _qubit(QubitState.ZERO)
        toffoli(c1, c2, t)
        self.assertEqual(t.state, QubitState.ONE)
        self.assertIsNone(t.entangle_group)

    def test_one_control_does_not_flip(self):
        c1 = _qubit(QubitState.ONE)
        c2 = _qubit(QubitState.ZERO)
        t = _qubit(QubitState.ZERO)
        toffoli(c1, c2, t)
        self.assertEqual(t.state, QubitState.ZERO)

    def test_superposed_control_entangles_target(self):
        c1 = _qubit(QubitState.SUPERPOSITION)
        c2 = _qubit(QubitState.ONE)
        t = _qubit(QubitState.ZERO)
        toffoli(c1, c2, t)
        self.assertEqual(t.state, QubitState.SUPERPOSITION)
        self.assertEqual(c1.entangle_group, t.entangle_group)
        self.assertIsNone(c2.entangle_group)


class TestAlgorithmBlocks(unittest.TestCase):

    def setUp(self):
        reset_world()

    def test_qft_preserves_quarter_turn_phase(self):
        c = _qubit(QubitState.ZERO)
        t = _qubit(QubitState.ONE)
        qft(c, t)
        self.assertEqual(c.state, QubitState.SUPERPOSITION)
        self.assertEqual(t.state, QubitState.SUPERPOSITION)
        self.assertAlmostEqual(abs(t.phase_angle), math.pi / 2)

    def test_grover_amplifies_marked_state(self):
        c = _qubit(QubitState.SUPERPOSITION)
        t = _qubit(QubitState.SUPERPOSITION)
        grover(c, t)
        self.assertEqual(c.state, QubitState.ONE)
        self.assertEqual(t.state, QubitState.ONE)

    def test_toy_shor_uses_qft_readout(self):
        c = _qubit(QubitState.ZERO)
        t = _qubit(QubitState.ZERO)
        shor(c, t)
        self.assertEqual(c.state, QubitState.SUPERPOSITION)
        self.assertEqual(t.state, QubitState.SUPERPOSITION)

    def test_teleport_moves_source_state_to_target(self):
        helper = _qubit(QubitState.ZERO)
        source = _qubit(QubitState.SUPERPOSITION)
        source.beta *= 1j
        target = _qubit(QubitState.ZERO)
        teleport(helper, source, target)
        self.assertEqual(target.state, QubitState.SUPERPOSITION)
        self.assertAlmostEqual(target.phase_angle, math.pi / 2)
        self.assertEqual(source.state, QubitState.ZERO)
        self.assertEqual(helper.state, QubitState.ZERO)


# Measurement

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

    def test_measurement_history_scales_with_tile_size(self):
        from src.engine.gates.measurement import _overlay

        def history_heights(tile_size):
            calls = []
            draw_rect = pygame.draw.rect

            def spy(surface, color, rect, *args, **kwargs):
                calls.append(pygame.Rect(rect))
                return calls[-1]

            tile = _tile(measurements=[QubitState.ZERO] * 20)
            try:
                pygame.draw.rect = spy
                _overlay(pygame.Surface((tile_size, tile_size), pygame.SRCALPHA),
                         pygame.Rect(0, 0, tile_size, tile_size), tile)
            finally:
                pygame.draw.rect = draw_rect
            return [r.height for r in calls[2:]]

        self.assertLess(max(history_heights(20)), max(history_heights(64)))

    def test_measure_flash_set(self):
        q = _qubit(QubitState.ZERO)
        tile = _tile()
        measure(q, tile)
        self.assertAlmostEqual(tile.measure_flash, 0.35)

    def test_sink_counts_superposition_without_measuring(self):
        from src.engine.simulation import _collect_sink
        q = _qubit(QubitState.SUPERPOSITION)
        tile = _tile(sink_target=QubitState.SUPERPOSITION)
        _collect_sink(tile, q)
        self.assertEqual(tile.sink_total, 1)
        self.assertEqual(tile.sink_match, 1)


# Splitter

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
        """When gate faces DOWN, |0> goes (0,1) and |1> goes (-1,0)."""
        _, ej_zero = self._run_splitter(QubitState.ZERO, Direction.DOWN)
        self.assertEqual(ej_zero[0][:2], (0, 1))
        _, ej_one = self._run_splitter(QubitState.ONE, Direction.DOWN)
        self.assertEqual(ej_one[0][:2], (-1, 0))


# Entanglement registry

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
        hadamard(q1)  # H|+> = |0>, breaks entanglement
        self.assertIsNone(q1.entangle_group)


# Safe transform (error handling in simulation)

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


class TestInputHandler(unittest.TestCase):

    def test_right_drag_deletes_tiles(self):
        from src.core import config
        from src.core.world import get_tile
        from src.engine.gate_registry import BELT, EMPTY
        from src.ui.input_handler import handle_input

        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()
        pygame.display.set_mode((1, 1))
        old_size = config.WIDTH, config.HEIGHT
        try:
            config.WIDTH, config.HEIGHT = 320, 240
            reset_world()
            get_tile(0, 0).building = BELT
            get_tile(1, 0).building = BELT
            handle_input(0, BELT, Direction.RIGHT, False, False, [
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(5, 5)),
                pygame.event.Event(pygame.MOUSEMOTION, pos=(config.TILE_SIZE + 5, 5)),
                pygame.event.Event(pygame.MOUSEBUTTONUP, button=3, pos=(config.TILE_SIZE + 5, 5)),
            ])
            self.assertEqual(get_tile(0, 0).building, EMPTY)
            self.assertEqual(get_tile(1, 0).building, EMPTY)
        finally:
            config.WIDTH, config.HEIGHT = old_size


class TestProgressMeta(unittest.TestCase):

    def test_xp_and_achievements_are_derived_from_completed_levels(self):
        from src.ui import menu

        old = set(menu.completed_levels)
        try:
            menu.completed_levels.clear()
            self.assertEqual(menu.xp_total(), 0)
            self.assertEqual(menu.achievements(), [])
            menu.completed_levels.add(0)
            self.assertEqual(menu.xp_total(), 100)
            self.assertIn("First Clear", menu.achievements())
        finally:
            menu.completed_levels.clear()
            menu.completed_levels.update(old)


class TestCircuitExport(unittest.TestCase):

    def _two_cell_script(self, building):
        from src.engine.circuit_export import generate_qiskit_script
        from src.engine.gate_registry import BELT, GENERATOR, OUTPUT_SINK

        grid = {}

        def put(pos, bid, peer=None, is_ctrl=False):
            grid[pos] = _tile(
                building=bid,
                direction=Direction.RIGHT,
                peer=peer,
                is_ctrl=is_ctrl,
            )

        put((0, 0), GENERATOR)
        put((1, 0), BELT)
        put((2, 0), building, peer=(2, 1), is_ctrl=True)
        put((3, 0), OUTPUT_SINK)
        put((0, 1), GENERATOR)
        put((1, 1), BELT)
        put((2, 1), building, peer=(2, 0))
        put((3, 1), OUTPUT_SINK)
        return generate_qiskit_script(grid)

    def _three_cell_script(self):
        from src.engine.circuit_export import generate_qiskit_script
        from src.engine.gate_registry import BELT, GENERATOR, OUTPUT_SINK

        grid = {}

        def put(pos, bid, peer=None, is_ctrl=False, role=1):
            grid[pos] = _tile(
                building=bid,
                direction=Direction.RIGHT,
                peer=peer,
                is_ctrl=is_ctrl,
                role=role,
            )

        for y in range(3):
            put((0, y), GENERATOR)
            put((1, y), BELT)
            put((3, y), OUTPUT_SINK)
        put((2, 0), "toffoli", peer=(2, 2), is_ctrl=True, role=3)
        put((2, 1), "toffoli", peer=(2, 2), is_ctrl=True, role=2)
        put((2, 2), "toffoli", peer=(2, 1), role=1)
        return generate_qiskit_script(grid)

    def test_two_cell_gates_export_as_two_qubit_ops(self):
        expected = {"cnot": "cx", "cz": "cz", "swap": "swap"}
        for building, qiskit_name in expected.items():
            script = self._two_cell_script(building)
            self.assertIn(f"qc.{qiskit_name}(0, 1)", script)
            self.assertNotIn("WARNING", script)

    def test_toffoli_exports_as_ccx(self):
        script = self._three_cell_script()
        self.assertIn("qc.ccx(1, 0, 2)", script)
        self.assertNotIn("WARNING", script)

    def test_unknown_multi_gate_export_warns_instead_of_cnot(self):
        script = self._two_cell_script("qft")
        self.assertIn("WARNING: qft", script)
        self.assertNotIn("qc.cx", script)


if __name__ == "__main__":
    unittest.main()
