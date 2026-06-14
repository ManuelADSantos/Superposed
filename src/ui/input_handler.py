"""Input handling: keyboard, mouse, and toolbar interaction."""

from __future__ import annotations

import pygame
from ..core import config
from ..core.config import TILE_SIZE, TOOLBAR_HEIGHT, TOOLBAR_PAD
from ..core.entities import Direction, QubitState, cw_dir
from ..core.world import screen_to_world, get_tile, in_bounds
from ..engine.gate_registry import get_gate, active_toolbar, EMPTY, OUTPUT_SINK
from ..engine.circuit_export import export_circuit
from .rendering import get_export_button_rect, show_toast
from ..core import world as W


def _toolbar_hit(mx, my):
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    if my < tb_y:
        return None
    active = active_toolbar(W.available_buildings)
    btn_size = TOOLBAR_HEIGHT - 2 * TOOLBAR_PAD
    start_x = max(TOOLBAR_PAD, (config.WIDTH - len(active) * (btn_size + TOOLBAR_PAD)) // 2)
    for i, gid in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)
        if rect.collidepoint(mx, my):
            return gid
    return None


def _build_key_map():
    active = active_toolbar(W.available_buildings)
    km = {}
    for idx, gid in enumerate(active):
        key_code = getattr(pygame, f"K_{idx + 1}", None)
        if key_code:
            km[key_code] = gid
    return km


def handle_input(dt, selected_building, selected_rotation, paused, step_requested,
                 events=None):
    """Process keyboard/mouse input.

    *events* is the list of pygame events for this frame.  If ``None``
    (legacy call), events are pulled from the pygame queue — but passing
    them explicitly is preferred so the main loop doesn't need to re-post.
    """
    back_to_menu = False

    keys = pygame.key.get_pressed()
    speed = 600 * dt
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        W._state.camera_y -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        W._state.camera_y += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        W._state.camera_x -= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        W._state.camera_x += speed

    key_map = _build_key_map()

    if events is None:
        events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            return False, selected_building, selected_rotation, paused, step_requested, False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True, selected_building, selected_rotation, paused, step_requested, True

            if event.key in key_map:
                selected_building = key_map[event.key]
            elif event.key == pygame.K_r:
                selected_rotation = cw_dir(selected_rotation)
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_n and paused:
                step_requested = True
            elif event.key == pygame.K_c:
                for pos in list(W.world.keys()):
                    if pos not in W.locked_tiles:
                        del W.world[pos]
            elif event.key == pygame.K_TAB:
                back_to_menu = True

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            old_zoom = W._state.zoom
            W._state.zoom = max(0.3, min(3.0, W._state.zoom + event.y * 0.12))
            factor = W._state.zoom / old_zoom
            W._state.camera_x = mx + (W._state.camera_x - mx) * factor
            W._state.camera_y = my + (W._state.camera_y - my) * factor

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Export button
            if event.button == 1 and get_export_button_rect().collidepoint(mx, my):
                try:
                    path = export_circuit()
                    show_toast(f"Exported to {path}")
                except Exception as exc:
                    show_toast(f"Export failed: {exc}")
                continue

            tb_hit = _toolbar_hit(mx, my)
            if tb_hit is not None:
                selected_building = tb_hit
                continue

            if my < config.HEIGHT - TOOLBAR_HEIGHT:
                wx, wy = screen_to_world(mx, my, TILE_SIZE)
                if in_bounds(wx, wy):
                    tile = get_tile(wx, wy)
                    is_locked = (wx, wy) in W.locked_tiles

                    if event.button == 1 and not is_locked:
                        if W.available_buildings is None or selected_building in W.available_buildings:
                            tile.building = selected_building
                            tile.direction = selected_rotation
                            tile.control_item = None
                            tile.process_timer = 0.0
                            if selected_building == OUTPUT_SINK:
                                tile.sink_total = 0
                                tile.sink_match = 0
                                tile.sink_target = None

                    elif event.button == 3 and not is_locked:
                        tile.building = EMPTY
                        tile.item = None
                        tile.control_item = None

                    elif event.button == 2:
                        if tile.building == OUTPUT_SINK and not is_locked:
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

    active = active_toolbar(W.available_buildings)
    if active and selected_building not in active:
        selected_building = active[0]

    return True, selected_building, selected_rotation, paused, step_requested, back_to_menu
