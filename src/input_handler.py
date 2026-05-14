"""Input handling: keyboard, mouse, and toolbar interaction."""

import pygame

import config
from config import TILE_SIZE, TOOLBAR_HEIGHT, TOOLBAR_PAD
from entities import (
    BuildingType, Direction, QubitState,
    TOOLBAR_ORDER, BUILDING_INFO,
)
from world import screen_to_world, get_tile, in_bounds
import world as W


def _rotate_cw(d: Direction) -> Direction:
    return Direction((d.value + 1) % 4)


def _active_toolbar():
    """Return the toolbar buildings available in the current mode."""
    if W.available_buildings is not None:
        return [b for b in TOOLBAR_ORDER if b in W.available_buildings]
    return list(TOOLBAR_ORDER)


def _toolbar_hit(mx, my):
    """Return the BuildingType clicked in the toolbar, or None."""
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    if my < tb_y:
        return None
    active = _active_toolbar()
    btn_size = TOOLBAR_HEIGHT - 2 * TOOLBAR_PAD
    total = len(active)
    start_x = max(TOOLBAR_PAD, (config.WIDTH - total * (btn_size + TOOLBAR_PAD)) // 2)
    for i, bt in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)
        if rect.collidepoint(mx, my):
            return bt
    return None


def _build_key_map():
    """Build key → BuildingType map based on current available buildings."""
    active = _active_toolbar()
    km = {}
    for idx, bt in enumerate(active):
        key_code = getattr(pygame, f"K_{idx + 1}", None)
        if key_code:
            km[key_code] = bt
    return km


def handle_input(dt, selected_building, selected_rotation, paused, step_requested):
    """Process events and return updated state tuple.

    Returns: (running, selected_building, selected_rotation, paused,
              step_requested, back_to_menu)
    """
    back_to_menu = False

    # Continuous camera movement
    keys = pygame.key.get_pressed()
    speed = 600 * dt
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        W.camera_y -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        W.camera_y += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        W.camera_x -= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        W.camera_x += speed

    key_map = _build_key_map()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, selected_building, selected_rotation, paused, step_requested, False

        # ----- Keyboard -----
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Always go back to main menu
                return True, selected_building, selected_rotation, paused, step_requested, True

            if event.key in key_map:
                selected_building = key_map[event.key]

            elif event.key == pygame.K_r:
                selected_rotation = _rotate_cw(selected_rotation)

            elif event.key == pygame.K_p:
                paused = not paused

            elif event.key == pygame.K_n and paused:
                step_requested = True

            elif event.key == pygame.K_c:
                # Clear non-locked tiles
                for pos in list(W.world.keys()):
                    if pos not in W.locked_tiles:
                        del W.world[pos]

            elif event.key == pygame.K_TAB:
                # Quick back to menu
                back_to_menu = True

        # ----- Mouse wheel (zoom) -----
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            old_zoom = W.zoom
            W.zoom = max(0.3, min(3.0, W.zoom + event.y * 0.12))
            factor = W.zoom / old_zoom
            W.camera_x = mx + (W.camera_x - mx) * factor
            W.camera_y = my + (W.camera_y - my) * factor

        # ----- Mouse click -----
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Toolbar click?
            tb_hit = _toolbar_hit(mx, my)
            if tb_hit is not None:
                selected_building = tb_hit
                continue

            # World click (only above toolbar)
            if my < config.HEIGHT - TOOLBAR_HEIGHT:
                wx, wy = screen_to_world(mx, my, TILE_SIZE)
                if in_bounds(wx, wy):
                    tile = get_tile(wx, wy)
                    is_locked = (wx, wy) in W.locked_tiles

                    if event.button == 1 and not is_locked:
                        # Check building is allowed
                        if W.available_buildings is None or selected_building in W.available_buildings:
                            tile.building = selected_building
                            tile.direction = selected_rotation
                            tile.control_item = None
                            tile.process_timer = 0.0
                            if selected_building == BuildingType.OUTPUT_SINK:
                                tile.sink_total = 0
                                tile.sink_match = 0
                                tile.sink_target = None

                    elif event.button == 3 and not is_locked:
                        tile.building = BuildingType.EMPTY
                        tile.item = None
                        tile.control_item = None

                    elif event.button == 2:
                        if tile.building == BuildingType.OUTPUT_SINK and not is_locked:
                            # Cycle sink target
                            if tile.sink_target is None:
                                tile.sink_target = QubitState.ZERO
                            elif tile.sink_target == QubitState.ZERO:
                                tile.sink_target = QubitState.ONE
                            elif tile.sink_target == QubitState.ONE:
                                tile.sink_target = QubitState.SUPERPOSITION
                            else:
                                tile.sink_target = None
                            tile.sink_total = 0
                            tile.sink_match = 0

    # Ensure selected building is still valid for current mode
    active = _active_toolbar()
    if active and selected_building not in active:
        selected_building = active[0]

    return True, selected_building, selected_rotation, paused, step_requested, back_to_menu
