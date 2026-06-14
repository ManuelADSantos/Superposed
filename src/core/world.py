"""World grid, camera, entanglement registry, and level state.

All mutable state lives in a single WorldState instance (_state).
Camera/zoom are always accessed via ``_state`` directly.
Module-level names expose mutable containers (world, entangle_groups,
locked_tiles, available_buildings) and are re-bound on reset/load.
Call ``reset_world()`` to reinitialise cleanly.
"""

from __future__ import annotations

from .entities import Tile, QubitItem, QubitState
from ..engine.gate_registry import EMPTY, OUTPUT_SINK


# ═══════════════════════════════════════════════════════════════════════════
# WorldState — all mutable game state in one place
# ═══════════════════════════════════════════════════════════════════════════

class WorldState:
    """Encapsulates the entire mutable state of a game session."""

    def __init__(self):
        # Sparse infinite grid
        self.world: dict[tuple[int, int], Tile] = {}

        # Camera
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.zoom: float = 1.0

        # ── Entanglement registry ──────────────────────────────────────
        # Simplified model: only same-state correlation (|00> + |11>).
        # When one partner is measured, all others collapse to the SAME
        # outcome.  Anti-correlated Bell states (|01> + |10>) are not
        # modeled.  Applying gates (e.g. X) to an entangled qubit
        # changes its local state but does NOT update the correlation
        # rule — a deliberate simplification for the tutorial scope.
        self._next_entangle_id: int = 0
        self.entangle_groups: dict[int, set[int]] = {}
        self.entangle_lookup: dict[int, QubitItem] = {}

        # Level state
        self.current_level_index: int | None = None
        self.current_level_def: dict | None = None
        self.locked_tiles: set[tuple[int, int]] = set()
        self.available_buildings: list[str] | None = None

    # ── Entanglement helpers ───────────────────────────────────────────

    def create_entangle_group(self) -> int:
        self._next_entangle_id += 1
        self.entangle_groups[self._next_entangle_id] = set()
        return self._next_entangle_id

    def register_entangled(self, group_id: int, qubit: QubitItem):
        qubit.entangle_group = group_id
        self.entangle_groups.setdefault(group_id, set()).add(qubit.uid)
        self.entangle_lookup[qubit.uid] = qubit

    def get_entangled_partners(self, qubit: QubitItem) -> list[QubitItem]:
        if qubit.entangle_group is None:
            return []
        return [
            self.entangle_lookup[uid]
            for uid in self.entangle_groups.get(qubit.entangle_group, set())
            if uid != qubit.uid and uid in self.entangle_lookup
        ]

    def break_entanglement(self, qubit: QubitItem):
        gid = qubit.entangle_group
        if gid is not None and gid in self.entangle_groups:
            self.entangle_groups[gid].discard(qubit.uid)
            if not self.entangle_groups[gid]:
                del self.entangle_groups[gid]
        self.entangle_lookup.pop(qubit.uid, None)
        qubit.entangle_group = None

    # ── Tile helpers ───────────────────────────────────────────────────

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


# ═══════════════════════════════════════════════════════════════════════════
# Active instance + module-level proxies (backward compatibility)
# ═══════════════════════════════════════════════════════════════════════════

_state = WorldState()


# --- module-level names (re-bound on reset/load) -------------------------

world          = _state.world
entangle_groups = _state.entangle_groups
entangle_lookup = _state.entangle_lookup

current_level_index  = _state.current_level_index
current_level_def    = _state.current_level_def
locked_tiles         = _state.locked_tiles
available_buildings  = _state.available_buildings


# --- proxy functions (delegate to the active WorldState) -----------------

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


# ═══════════════════════════════════════════════════════════════════════════
# Reset / Load — update module-level names so existing code sees changes
# ═══════════════════════════════════════════════════════════════════════════

def _sync_from_state():
    """Copy level/lock/available attributes from _state to module globals."""
    from . import world as _self
    _self.current_level_index = _state.current_level_index
    _self.current_level_def   = _state.current_level_def
    _self.locked_tiles        = _state.locked_tiles
    _self.available_buildings = _state.available_buildings


def reset_world():
    global current_level_index, current_level_def
    global locked_tiles, available_buildings

    _state.__init__()                     # reinitialise everything

    # Re-bind the module-level mutable containers to the NEW dicts/sets
    from . import world as _self
    _self.world           = _state.world
    _self.entangle_groups = _state.entangle_groups
    _self.entangle_lookup = _state.entangle_lookup

    _sync_from_state()

    # Evict stale sprite caches from the previous session
    from ..ui.sprites import clear_sprite_caches
    clear_sprite_caches()


def load_level(level_def, level_index):
    global current_level_index, current_level_def
    global locked_tiles, available_buildings

    reset_world()

    _state.current_level_index = level_index
    _state.current_level_def   = level_def
    _state.locked_tiles        = set(level_def.get("locked", set()))
    _state.available_buildings = list(level_def.get("available", []))

    for (x, y), data in level_def.get("pre_placed", {}).items():
        tile = _state.get_tile(x, y)
        tile.building = data[0]
        tile.direction = data[1]
        if len(data) > 2 and data[2] is not None:
            if tile.building == OUTPUT_SINK:
                tile.sink_target = data[2]

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
    for (x, y) in _state.locked_tiles:
        tile = _state.get_tile(x, y)
        if tile.building == OUTPUT_SINK:
            if tile.sink_target is None:
                if tile.sink_total >= win_count:
                    return True
            else:
                if tile.sink_match >= win_count:
                    return True
    return False
