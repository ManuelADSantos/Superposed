"""Simulation: qubit movement and item updates."""

from config import BELT_SPEED, GENERATOR_SPEED
from entities import BuildingType, QubitState, QubitItem, DIR_VECTORS
from world import get_tile, in_bounds, world
from gates import transform_qubit, record_measurement


def update_items(dt):
    """Update all items in the world."""
    moved_items = []

    # First pass: update progress and spawning
    for (x, y), tile in list(world.items()):
        if tile.measure_flash > 0:
            tile.measure_flash = max(0.0, tile.measure_flash - dt)

        if tile.item and tile.item.is_disappearing:
            tile.item.disappear_time -= dt
            if tile.item.disappear_time <= 0:
                tile.item = None

        if tile.building == BuildingType.GENERATOR:
            tile.spawn_timer += dt

            if tile.spawn_timer >= GENERATOR_SPEED:
                tile.spawn_timer = 0

                if tile.item is None:
                    tile.item = QubitItem(QubitState.ZERO)

        if tile.item:
            tile.item.progress += BELT_SPEED * dt

            if tile.item.progress >= 1.0:
                moved_items.append((x, y))

    # Second pass: move items to next tile
    for x, y in moved_items:
        tile = get_tile(x, y)

        if not tile.item:
            continue

        dx, dy = DIR_VECTORS[tile.direction]
        nx = x + dx
        ny = y + dy

        item = tile.item
        item.progress = 0

        if not in_bounds(nx, ny):
            item.is_disappearing = True
            item.disappear_time = 0.3
            continue

        next_tile = get_tile(nx, ny)

        # Apply gate transformations
        if next_tile.building in (
            BuildingType.HADAMARD,
            BuildingType.X_GATE,
            BuildingType.MEASUREMENT,
        ):
            outcome = transform_qubit(next_tile.building, item)

            if next_tile.building == BuildingType.MEASUREMENT:
                record_measurement(next_tile, outcome)
                tile.item = None
                continue

        # Move item to next tile
        if next_tile.building != BuildingType.EMPTY and next_tile.item is None:
            next_tile.item = item
            tile.item = None
