"""World and grid management."""

from entities import Tile

# Global world dictionary (sparse, infinite grid)
world = {}

# Camera and viewport state
camera_x = 0
camera_y = 0
zoom = 1.0


def get_tile(x, y):
    """Get or create a tile at the given world coordinates."""
    key = (x, y)
    if key not in world:
        world[key] = Tile()
    return world[key]


def in_bounds(x, y):
    """Check if coordinates are valid (always true for infinite grid)."""
    return True


def world_to_screen(wx, wy, tile_size):
    """Convert world coordinates to screen coordinates."""
    size = tile_size * zoom
    sx = (wx * size) - camera_x
    sy = (wy * size) - camera_y
    return sx, sy


def screen_to_world(sx, sy, tile_size):
    """Convert screen coordinates to world coordinates."""
    size = tile_size * zoom
    wx = int((sx + camera_x) // size)
    wy = int((sy + camera_y) // size)
    return wx, wy
