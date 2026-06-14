"""World grid, camera, entanglement registry, and level state.

All mutable state lives in a single WorldState instance (_state).
Module-level names (world, locked_tiles, etc.) are re-bound on
reset/load so that `import world as W; W.world` always resolves
to the current dict.
"""

from __future__ import annotations

from .entities import Tile, QubitItem, QubitState
from ..engine.gate_registry import EMPTY, OUTPUT_SINK


class WorldState:
    def __init__(self):
        self.world: dict[tuple[int, int], Tile] = {}
        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.zoom: float = 1.0

        # Entanglement: same-state correlation only (|00> + |11>).
        self._next_entangle_id: int = 0
        self.entangle_groups: dict[int, set[int]] = {}
        self.entangle_lookup: dict[int, QubitItem] = {}

        self.current_level_index: int | None = None
        self.current_level_def: dict | None = None
        self.locked_tiles: set[tuple[int, int]] = set()
        self.available_buildings: list[str] | None = None

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


# Proxy functions — delegate to _state
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


def _sync_from_state():
    from . import world as _self
    _self.current_level_index = _state.current_level_index
    _self.current_level_def   = _state.current_level_def
    _self.locked_tiles        = _state.locked_tiles
    _self.available_buildings = _state.available_buildings


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
