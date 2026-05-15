"""World grid, camera, entanglement registry, and level state."""

from __future__ import annotations
from entities import Tile, QubitItem, QubitState
from gate_registry import EMPTY, OUTPUT_SINK


# ---------------------------------------------------------------------------
# Sparse infinite grid
# ---------------------------------------------------------------------------
world: dict[tuple[int, int], Tile] = {}

camera_x = 0.0
camera_y = 0.0
zoom = 1.0

# ---------------------------------------------------------------------------
# Entanglement registry
# ---------------------------------------------------------------------------
_next_entangle_id = 0
entangle_groups: dict[int, set[int]] = {}
entangle_lookup: dict[int, QubitItem] = {}


def create_entangle_group() -> int:
    global _next_entangle_id
    _next_entangle_id += 1
    entangle_groups[_next_entangle_id] = set()
    return _next_entangle_id


def register_entangled(group_id: int, qubit: QubitItem):
    qubit.entangle_group = group_id
    entangle_groups.setdefault(group_id, set()).add(qubit.uid)
    entangle_lookup[qubit.uid] = qubit


def get_entangled_partners(qubit: QubitItem) -> list[QubitItem]:
    if qubit.entangle_group is None:
        return []
    return [
        entangle_lookup[uid]
        for uid in entangle_groups.get(qubit.entangle_group, set())
        if uid != qubit.uid and uid in entangle_lookup
    ]


def break_entanglement(qubit: QubitItem):
    gid = qubit.entangle_group
    if gid is not None and gid in entangle_groups:
        entangle_groups[gid].discard(qubit.uid)
        if not entangle_groups[gid]:
            del entangle_groups[gid]
    entangle_lookup.pop(qubit.uid, None)
    qubit.entangle_group = None


# ---------------------------------------------------------------------------
# Tile helpers
# ---------------------------------------------------------------------------

def get_tile(x, y) -> Tile:
    key = (x, y)
    if key not in world:
        world[key] = Tile()
    return world[key]


def in_bounds(x, y) -> bool:
    return True


def world_to_screen(wx, wy, tile_size):
    size = tile_size * zoom
    return (wx * size) - camera_x, (wy * size) - camera_y


def screen_to_world(sx, sy, tile_size):
    size = tile_size * zoom
    return int((sx + camera_x) // size), int((sy + camera_y) // size)


# ---------------------------------------------------------------------------
# Level state
# ---------------------------------------------------------------------------
current_level_index: int | None = None
current_level_def: dict | None = None
locked_tiles: set[tuple[int, int]] = set()
available_buildings: list[str] | None = None   # list of gate IDs, or None = all


def reset_world():
    global camera_x, camera_y, zoom, _next_entangle_id
    global current_level_index, current_level_def
    global locked_tiles, available_buildings
    world.clear()
    entangle_groups.clear()
    entangle_lookup.clear()
    _next_entangle_id = 0
    camera_x = 0.0
    camera_y = 0.0
    zoom = 1.0
    current_level_index = None
    current_level_def = None
    locked_tiles = set()
    available_buildings = None


def load_level(level_def, level_index):
    global current_level_index, current_level_def
    global locked_tiles, available_buildings
    global camera_x, camera_y, zoom

    reset_world()
    current_level_index = level_index
    current_level_def = level_def
    locked_tiles = set(level_def.get("locked", set()))
    available_buildings = list(level_def.get("available", []))

    for (x, y), data in level_def.get("pre_placed", {}).items():
        tile = get_tile(x, y)
        tile.building = data[0]       # string gate ID
        tile.direction = data[1]
        if len(data) > 2 and data[2] is not None:
            if tile.building == OUTPUT_SINK:
                tile.sink_target = data[2]

    cx, cy = level_def.get("camera", (0, 0))
    import config as _cfg
    zoom = 1.0
    camera_x = cx * _cfg.TILE_SIZE - _cfg.WIDTH / 2
    camera_y = cy * _cfg.TILE_SIZE - (_cfg.HEIGHT - _cfg.TOOLBAR_HEIGHT) / 2


def check_win_condition() -> bool:
    if current_level_def is None:
        return False
    win_count = current_level_def.get("win_count", 5)
    for (x, y) in locked_tiles:
        tile = get_tile(x, y)
        if tile.building == OUTPUT_SINK:
            if tile.sink_target is None:
                if tile.sink_total >= win_count:
                    return True
            else:
                if tile.sink_match >= win_count:
                    return True
    return False
