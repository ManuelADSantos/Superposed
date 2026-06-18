"""World grid, camera, entanglement registry, quantum operations, and level state.

All mutable state lives in a single WorldState instance (_state).
Module-level names (world, locked_tiles, etc.) are re-bound on
reset/load so that `import world as W; W.world` always resolves
to the current dict.
"""

from __future__ import annotations

import math
import random

from .entities import Tile, QubitItem, QubitState
from ..engine.gate_registry import EMPTY, OUTPUT_SINK


# ---------------------------------------------------------------------------
# Entangle group — holds joint state vector for correlated qubits
# ---------------------------------------------------------------------------

class EntangleGroup:
    __slots__ = ('qubit_order', 'statevec')

    def __init__(self):
        self.qubit_order: list[int] = []
        self.statevec: list[complex] = []


# ---------------------------------------------------------------------------
# World state
# ---------------------------------------------------------------------------

class WorldState:
    def __init__(self):
        self.world: dict[tuple[int, int], Tile] = {}
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.zoom: float = 1.0

        self._next_entangle_id: int = 0
        self.entangle_groups: dict[int, EntangleGroup] = {}
        self.entangle_lookup: dict[int, QubitItem] = {}

        self.current_level_index: int | None = None
        self.current_level_def: dict | None = None
        self.locked_tiles: set[tuple[int, int]] = set()
        self.available_buildings: list[str] | None = None
        self.gate_limits: dict[str, int] = {}

    def create_entangle_group(self) -> int:
        self._next_entangle_id += 1
        self.entangle_groups[self._next_entangle_id] = EntangleGroup()
        return self._next_entangle_id

    def register_entangled(self, group_id: int, qubit: QubitItem):
        """Add qubit to group, extending state vector via tensor product."""
        qubit.entangle_group = group_id
        group = self.entangle_groups[group_id]
        if not group.qubit_order:
            group.qubit_order.append(qubit.uid)
            group.statevec = [qubit.alpha, qubit.beta]
        else:
            new_sv = []
            for a in group.statevec:
                new_sv.append(a * qubit.alpha)
                new_sv.append(a * qubit.beta)
            group.qubit_order.append(qubit.uid)
            group.statevec = new_sv
        self.entangle_lookup[qubit.uid] = qubit

    def get_entangled_partners(self, qubit: QubitItem) -> list[QubitItem]:
        if qubit.entangle_group is None:
            return []
        group = self.entangle_groups.get(qubit.entangle_group)
        if group is None:
            return []
        return [
            self.entangle_lookup[uid]
            for uid in group.qubit_order
            if uid != qubit.uid and uid in self.entangle_lookup
        ]

    def break_entanglement(self, qubit: QubitItem):
        """Remove qubit from its group. Silently measures if entangled."""
        if qubit.entangle_group is None:
            return
        gid = qubit.entangle_group
        group = self.entangle_groups.get(gid)
        if group is None:
            qubit.entangle_group = None
            return
        if qubit.uid in group.qubit_order and len(group.qubit_order) > 1:
            _measure_from_group(qubit)
            return
        # Last qubit or not found — just clean up
        self.entangle_lookup.pop(qubit.uid, None)
        qubit.entangle_group = None
        if gid in self.entangle_groups:
            group.qubit_order = [u for u in group.qubit_order if u != qubit.uid]
            if not group.qubit_order:
                del self.entangle_groups[gid]

    def get_tile(self, x: int, y: int) -> Tile:
        key = (x, y)
        if key not in self.world:
            self.world[key] = Tile()
        return self.world[key]

    def world_to_screen(self, wx, wy, tile_size):
        size = tile_size * self.zoom
        return (wx * size) - self.camera_x, (wy * size) - self.camera_y

    def screen_to_world(self, sx, sy, tile_size):
        size = tile_size * self.zoom
        return int((sx + self.camera_x) // size), int((sy + self.camera_y) // size)


_state = WorldState()

# Module-level aliases — re-bound on reset/load, accessed as W.world etc.
world           = _state.world
entangle_groups = _state.entangle_groups
entangle_lookup = _state.entangle_lookup
current_level_index  = _state.current_level_index
current_level_def    = _state.current_level_def
locked_tiles         = _state.locked_tiles
available_buildings  = _state.available_buildings
gate_limits          = _state.gate_limits


# ---------------------------------------------------------------------------
# Quantum math — state vector operations
# ---------------------------------------------------------------------------

def _apply_1q_sv(sv, n, k, mat):
    """Apply 2×2 matrix to qubit at position k in n-qubit state vector."""
    bit = 1 << (n - 1 - k)
    for i in range(len(sv)):
        if i & bit:
            continue
        j = i | bit
        a, b = sv[i], sv[j]
        sv[i] = mat[0][0] * a + mat[0][1] * b
        sv[j] = mat[1][0] * a + mat[1][1] * b


def _apply_2q_sv(sv, n, k1, k2, mat):
    """Apply 4×4 matrix to qubits at positions k1, k2 in n-qubit state vector."""
    bit1 = 1 << (n - 1 - k1)
    bit2 = 1 << (n - 1 - k2)
    for i in range(len(sv)):
        if i & bit1 or i & bit2:
            continue
        i00, i01, i10, i11 = i, i | bit2, i | bit1, i | bit1 | bit2
        v = [sv[i00], sv[i01], sv[i10], sv[i11]]
        sv[i00] = sum(mat[0][c] * v[c] for c in range(4))
        sv[i01] = sum(mat[1][c] * v[c] for c in range(4))
        sv[i10] = sum(mat[2][c] * v[c] for c in range(4))
        sv[i11] = sum(mat[3][c] * v[c] for c in range(4))


def _apply_kq_sv(sv, n, ks, mat):
    """Apply a 2^k matrix to selected qubits in an n-qubit state vector."""
    bits = [1 << (n - 1 - k) for k in ks]
    dim = 1 << len(bits)
    for i in range(len(sv)):
        if any(i & bit for bit in bits):
            continue
        idxs = []
        for state in range(dim):
            idx = i
            for pos, bit in enumerate(bits):
                if state & (1 << (len(bits) - 1 - pos)):
                    idx |= bit
            idxs.append(idx)
        v = [sv[idx] for idx in idxs]
        for r, idx in enumerate(idxs):
            sv[idx] = sum(mat[r][c] * v[c] for c in range(dim))


def _is_sep_2q(sv):
    """Check if 2-qubit state vector is separable (product state)."""
    return abs(sv[0] * sv[3] - sv[1] * sv[2]) < 1e-10


def _extract_2q(sv):
    """Factor separable 2-qubit state into individual (alpha, beta) pairs."""
    a, b, c, d = sv
    p0 = abs(a) ** 2 + abs(b) ** 2
    if p0 > 1e-20:
        n1 = math.sqrt(p0)
        alpha1 = complex(n1)
        alpha2 = a / n1
        beta2 = b / n1
        p1 = abs(c) ** 2 + abs(d) ** 2
        if p1 > 1e-20:
            beta1 = c / alpha2 if abs(alpha2) > 1e-10 else d / beta2
        else:
            beta1 = 0 + 0j
    else:
        p1 = abs(c) ** 2 + abs(d) ** 2
        n1 = math.sqrt(p1)
        alpha1 = 0 + 0j
        beta1 = complex(n1)
        alpha2 = c / n1
        beta2 = d / n1
    return alpha1, beta1, alpha2, beta2


def _pure_qubit_pair(sv, n, k):
    bit = 1 << (n - 1 - k)
    p0 = sum(abs(sv[i]) ** 2 for i in range(len(sv)) if not (i & bit))
    p1 = 1 - p0
    rho_01 = sum(sv[i] * sv[i | bit].conjugate()
                 for i in range(len(sv)) if not (i & bit))
    if p0 * p1 - abs(rho_01) ** 2 > 1e-8:
        return None
    alpha = complex(math.sqrt(max(0, p0)))
    beta = rho_01.conjugate() / alpha if p0 > 1e-20 else 1 + 0j
    return alpha, beta


def _remove_product_qubit(sv, n, k, alpha, beta):
    bit = 1 << (n - 1 - k)
    want_one = abs(beta) > abs(alpha)
    amp = beta if want_one else alpha
    return [
        sv[i] / amp
        for i in range(len(sv))
        if bool(i & bit) == want_one
    ]


def _update_reduced(qubit):
    """Refresh qubit's alpha/beta from its group's state vector (for display)."""
    gid = qubit.entangle_group
    if gid is None:
        return
    group = _state.entangle_groups.get(gid)
    if group is None:
        return
    k = group.qubit_order.index(qubit.uid)
    n = len(group.qubit_order)
    sv = group.statevec
    bit = 1 << (n - 1 - k)

    p0 = sum(abs(sv[i]) ** 2 for i in range(len(sv)) if not (i & bit))
    rho_01 = sum(sv[i] * sv[i | bit].conjugate()
                 for i in range(len(sv)) if not (i & bit))

    qubit.alpha = complex(math.sqrt(max(0, p0)))
    p1 = max(0, 1 - p0)
    if p0 > 1e-20 and p1 > 1e-20 and abs(rho_01) > 1e-12:
        qubit.beta = complex(math.sqrt(p1)) * rho_01.conjugate() / abs(rho_01)
    else:
        qubit.beta = complex(math.sqrt(p1))


def _try_separate_group(group):
    """If a 2-qubit group is separable, dissolve it into solo qubits."""
    if len(group.qubit_order) != 2:
        for uid in group.qubit_order:
            if uid in _state.entangle_lookup:
                _update_reduced(_state.entangle_lookup[uid])
        return
    if not _is_sep_2q(group.statevec):
        for uid in group.qubit_order:
            _update_reduced(_state.entangle_lookup[uid])
        return
    a1, b1, a2, b2 = _extract_2q(group.statevec)
    q1 = _state.entangle_lookup[group.qubit_order[0]]
    q2 = _state.entangle_lookup[group.qubit_order[1]]
    q1.alpha, q1.beta = a1, b1
    q2.alpha, q2.beta = a2, b2
    gid = q1.entangle_group
    q1.entangle_group = None
    q2.entangle_group = None
    _state.entangle_lookup.pop(q1.uid, None)
    _state.entangle_lookup.pop(q2.uid, None)
    _state.entangle_groups.pop(gid, None)


# ---------------------------------------------------------------------------
# Public quantum operations
# ---------------------------------------------------------------------------

def apply_single(qubit, mat):
    """Apply 2×2 unitary to a qubit. Handles solo and entangled cases."""
    if qubit.entangle_group is None:
        a, b = qubit.alpha, qubit.beta
        qubit.alpha = mat[0][0] * a + mat[0][1] * b
        qubit.beta = mat[1][0] * a + mat[1][1] * b
    else:
        group = _state.entangle_groups[qubit.entangle_group]
        k = group.qubit_order.index(qubit.uid)
        _apply_1q_sv(group.statevec, len(group.qubit_order), k, mat)
        _try_separate_group(group)


def apply_two(qubit_a, qubit_b, mat):
    """Apply 4×4 unitary to qubit pair. Handles all entanglement cases."""
    ga, gb = qubit_a.entangle_group, qubit_b.entangle_group

    if ga is None and gb is None:
        # Both solo — form tensor product, apply, check separability
        sv = [
            qubit_a.alpha * qubit_b.alpha,
            qubit_a.alpha * qubit_b.beta,
            qubit_a.beta * qubit_b.alpha,
            qubit_a.beta * qubit_b.beta,
        ]
        _apply_2q_sv(sv, 2, 0, 1, mat)
        if _is_sep_2q(sv):
            a1, b1, a2, b2 = _extract_2q(sv)
            qubit_a.alpha, qubit_a.beta = a1, b1
            qubit_b.alpha, qubit_b.beta = a2, b2
        else:
            gid = _state.create_entangle_group()
            group = _state.entangle_groups[gid]
            group.qubit_order = [qubit_a.uid, qubit_b.uid]
            group.statevec = sv
            qubit_a.entangle_group = gid
            qubit_b.entangle_group = gid
            _state.entangle_lookup[qubit_a.uid] = qubit_a
            _state.entangle_lookup[qubit_b.uid] = qubit_b
            _update_reduced(qubit_a)
            _update_reduced(qubit_b)
        return

    if ga is not None and ga == gb:
        # Same group — apply in-place
        group = _state.entangle_groups[ga]
        k1 = group.qubit_order.index(qubit_a.uid)
        k2 = group.qubit_order.index(qubit_b.uid)
        _apply_2q_sv(group.statevec, len(group.qubit_order), k1, k2, mat)
        _try_separate_group(group)
        return

    # Different groups or one solo — merge then apply
    # Collect state vectors
    if ga is not None:
        grp_a = _state.entangle_groups[ga]
        sv_a = grp_a.statevec
        order_a = list(grp_a.qubit_order)
    else:
        sv_a = [qubit_a.alpha, qubit_a.beta]
        order_a = [qubit_a.uid]

    if gb is not None:
        grp_b = _state.entangle_groups[gb]
        sv_b = grp_b.statevec
        order_b = list(grp_b.qubit_order)
    else:
        sv_b = [qubit_b.alpha, qubit_b.beta]
        order_b = [qubit_b.uid]

    # Tensor product: A ⊗ B
    merged_sv = []
    for a in sv_a:
        for b in sv_b:
            merged_sv.append(a * b)
    merged_order = order_a + order_b

    # Apply 2-qubit gate
    k1 = merged_order.index(qubit_a.uid)
    k2 = merged_order.index(qubit_b.uid)
    _apply_2q_sv(merged_sv, len(merged_order), k1, k2, mat)

    merged_lookup = {
        uid: _state.entangle_lookup[uid]
        for uid in merged_order
        if uid in _state.entangle_lookup
    }
    merged_lookup[qubit_a.uid] = qubit_a
    merged_lookup[qubit_b.uid] = qubit_b

    # Clean up old groups
    if ga is not None:
        for uid in order_a:
            _state.entangle_lookup.pop(uid, None)
        _state.entangle_groups.pop(ga, None)
    if gb is not None and gb != ga:
        for uid in order_b:
            _state.entangle_lookup.pop(uid, None)
        _state.entangle_groups.pop(gb, None)

    # Create merged group
    gid = _state.create_entangle_group()
    group = _state.entangle_groups[gid]
    group.qubit_order = merged_order
    group.statevec = merged_sv
    for uid in merged_order:
        q = merged_lookup.get(uid)
        if q:
            q.entangle_group = gid
            _state.entangle_lookup[uid] = q

    _try_separate_group(group)


def apply_many(qubits, mat):
    """Apply a multi-qubit unitary, merging/dissolving entangle groups as needed."""
    qubits = list(qubits)
    pieces = []
    lookup = {}
    old_groups = set()
    seen = set()

    for qubit in qubits:
        gid = qubit.entangle_group
        key = gid if gid is not None else ("solo", qubit.uid)
        if key in seen:
            continue
        seen.add(key)
        if gid is None:
            pieces.append(([qubit.uid], [qubit.alpha, qubit.beta]))
            lookup[qubit.uid] = qubit
        else:
            group = _state.entangle_groups[gid]
            order = list(group.qubit_order)
            pieces.append((order, list(group.statevec)))
            old_groups.add(gid)
            for uid in order:
                if uid in _state.entangle_lookup:
                    lookup[uid] = _state.entangle_lookup[uid]

    merged_order = []
    merged_sv = [1 + 0j]
    for order, sv in pieces:
        merged_sv = [a * b for a in merged_sv for b in sv]
        merged_order += order

    ks = [merged_order.index(qubit.uid) for qubit in qubits]
    _apply_kq_sv(merged_sv, len(merged_order), ks, mat)

    for gid in old_groups:
        group = _state.entangle_groups.pop(gid, None)
        if group:
            for uid in group.qubit_order:
                _state.entangle_lookup.pop(uid, None)

    solo = {}
    while len(merged_order) > 1:
        split = next(
            ((k, pair) for k in range(len(merged_order))
             if (pair := _pure_qubit_pair(merged_sv, len(merged_order), k)) is not None),
            None,
        )
        if split is None:
            break
        k, (alpha, beta) = split
        uid = merged_order.pop(k)
        solo[uid] = (alpha, beta)
        merged_sv = _remove_product_qubit(merged_sv, len(merged_order) + 1, k, alpha, beta)

    for uid, (alpha, beta) in solo.items():
        qubit = lookup.get(uid)
        if qubit:
            qubit.alpha, qubit.beta = alpha, beta
            qubit.entangle_group = None

    if len(merged_order) == 1:
        qubit = lookup.get(merged_order[0])
        if qubit:
            qubit.alpha, qubit.beta = merged_sv
            qubit.entangle_group = None
        return

    gid = _state.create_entangle_group()
    group = _state.entangle_groups[gid]
    group.qubit_order = merged_order
    group.statevec = merged_sv
    for uid in merged_order:
        qubit = lookup.get(uid)
        if qubit:
            qubit.entangle_group = gid
            _state.entangle_lookup[uid] = qubit
            _update_reduced(qubit)


def measure_qubit(qubit) -> QubitState:
    """Measure qubit in computational basis. Returns ZERO or ONE."""
    if qubit.entangle_group is None:
        p0 = abs(qubit.alpha) ** 2
        if random.random() < p0:
            qubit.alpha, qubit.beta = 1 + 0j, 0 + 0j
            return QubitState.ZERO
        else:
            qubit.alpha, qubit.beta = 0 + 0j, 1 + 0j
            return QubitState.ONE
    return _measure_from_group(qubit)


def _measure_from_group(qubit) -> QubitState:
    """Measure one qubit from an entangled group, collapsing the state vector."""
    gid = qubit.entangle_group
    group = _state.entangle_groups[gid]
    k = group.qubit_order.index(qubit.uid)
    n = len(group.qubit_order)
    sv = group.statevec
    bit = 1 << (n - 1 - k)

    p0 = sum(abs(sv[i]) ** 2 for i in range(len(sv)) if not (i & bit))
    result = 0 if random.random() < p0 else 1
    norm_sq = p0 if result == 0 else (1 - p0)
    norm = math.sqrt(norm_sq) if norm_sq > 1e-30 else 1.0

    # Build new state vector for remaining qubits
    new_order = [uid for uid in group.qubit_order if uid != qubit.uid]
    new_n = n - 1

    # Set measured qubit to collapsed state
    qubit.alpha = 1 + 0j if result == 0 else 0 + 0j
    qubit.beta = 0 + 0j if result == 0 else 1 + 0j
    qubit.entangle_group = None
    _state.entangle_lookup.pop(qubit.uid, None)

    if new_n == 0:
        _state.entangle_groups.pop(gid, None)
        return QubitState.ZERO if result == 0 else QubitState.ONE

    new_sv = [0j] * (1 << new_n)
    for old_i in range(len(sv)):
        if ((old_i >> (n - 1 - k)) & 1) != result:
            continue
        new_i = 0
        shift = 0
        for j in range(n):
            if j == k:
                continue
            if old_i & (1 << (n - 1 - j)):
                new_i |= (1 << (new_n - 1 - shift))
            shift += 1
        new_sv[new_i] = sv[old_i] / norm

    if new_n == 1:
        remaining_uid = new_order[0]
        remaining = _state.entangle_lookup[remaining_uid]
        remaining.alpha = new_sv[0]
        remaining.beta = new_sv[1]
        remaining.entangle_group = None
        _state.entangle_lookup.pop(remaining_uid, None)
        _state.entangle_groups.pop(gid, None)
    else:
        group.qubit_order = new_order
        group.statevec = new_sv
        for uid in new_order:
            _update_reduced(_state.entangle_lookup[uid])

    return QubitState.ZERO if result == 0 else QubitState.ONE


# ---------------------------------------------------------------------------
# Proxy functions — delegate to _state
# ---------------------------------------------------------------------------

def create_entangle_group() -> int:
    return _state.create_entangle_group()

def register_entangled(group_id: int, qubit: QubitItem):
    _state.register_entangled(group_id, qubit)

def get_entangled_partners(qubit: QubitItem) -> list[QubitItem]:
    return _state.get_entangled_partners(qubit)

def break_entanglement(qubit: QubitItem):
    _state.break_entanglement(qubit)

def get_tile(x, y) -> Tile:
    return _state.get_tile(x, y)

def world_to_screen(wx, wy, tile_size):
    return _state.world_to_screen(wx, wy, tile_size)

def screen_to_world(sx, sy, tile_size):
    return _state.screen_to_world(sx, sy, tile_size)


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def _sync_from_state():
    from . import world as _self
    _self.current_level_index = _state.current_level_index
    _self.current_level_def   = _state.current_level_def
    _self.locked_tiles        = _state.locked_tiles
    _self.available_buildings = _state.available_buildings
    _self.gate_limits        = _state.gate_limits


def reset_world():
    global current_level_index, current_level_def
    global locked_tiles, available_buildings

    _state.__init__()

    from . import world as _self
    _self.world           = _state.world
    _self.entangle_groups = _state.entangle_groups
    _self.entangle_lookup = _state.entangle_lookup
    _sync_from_state()

    from ..ui.sprites import clear_sprite_caches
    clear_sprite_caches()


def count_placed(building: str) -> int:
    """Count player-placed (non-locked, non-companion) instances of a gate."""
    return sum(
        1 for pos, tile in _state.world.items()
        if tile.building == building and not tile.is_ctrl and pos not in _state.locked_tiles
    )


def load_level(level_def, level_index):
    global current_level_index, current_level_def
    global locked_tiles, available_buildings, gate_limits

    reset_world()

    from ..engine.simulation import reset_spawn_clock
    reset_spawn_clock()

    _state.current_level_index = level_index
    _state.current_level_def   = level_def
    _state.locked_tiles        = set(level_def.get("locked", set()))
    _state.available_buildings = list(level_def.get("available", []))
    _state.gate_limits         = dict(level_def.get("gate_limits", {}))

    from ..engine.gate_registry import get_gate, Category
    from .entities import ccw_dir, DIR_VECTORS

    for (x, y), data in level_def.get("pre_placed", {}).items():
        tile = _state.get_tile(x, y)
        tile.building = data[0]
        tile.direction = data[1]
        tile.role = 1
        if len(data) > 2 and data[2] is not None:
            if tile.building == OUTPUT_SINK:
                target = data[2]
                if isinstance(target, tuple):
                    tile.sink_target, tile.sink_phase = target
                else:
                    tile.sink_target = target

    # Auto-create companions for pre-placed multi-qubit gates
    for (x, y), data in level_def.get("pre_placed", {}).items():
        gate = get_gate(data[0])
        if gate and gate.category == Category.TWO_QUBIT:
            direction = data[1]
            cd = ccw_dir(direction)
            dx, dy = DIR_VECTORS[cd]
            primary = _state.get_tile(x, y)
            primary.peer = (x + dx, y + dy)
            for role in range(2, gate.qubits + 1):
                cx, cy = x + dx * (role - 1), y + dy * (role - 1)
                companion = _state.get_tile(cx, cy)
                companion.building = data[0]
                companion.direction = direction
                companion.peer = (x, y)
                companion.is_ctrl = True
                companion.role = role
                _state.locked_tiles.add((cx, cy))

    cx, cy = level_def.get("camera", (0, 0))
    from . import config as _cfg
    _state.zoom     = 1.0
    _state.camera_x = cx * _cfg.TILE_SIZE - _cfg.WIDTH / 2
    _state.camera_y = cy * _cfg.TILE_SIZE - (_cfg.HEIGHT - _cfg.TOOLBAR_HEIGHT) / 2

    _sync_from_state()


def check_win_condition() -> bool:
    if _state.current_level_def is None:
        return False
    win_count = _state.current_level_def.get("win_count", 5)

    if _state.current_level_def.get("win_type") == "measure":
        total = sum(len(t.measurements) for t in _state.world.values()
                    if t.building == "measurement")
        return total >= win_count

    sinks = []
    for (x, y) in _state.locked_tiles:
        tile = _state.get_tile(x, y)
        if tile.building == OUTPUT_SINK:
            sinks.append(tile)
    if not sinks:
        return False
    return all(
        (t.sink_total if t.sink_target is None else t.sink_match) >= win_count
        for t in sinks
    )
