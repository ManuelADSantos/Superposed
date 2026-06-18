"""Input handling: keyboard, mouse, and toolbar interaction."""

from __future__ import annotations

import pygame
from ..core import config
from ..core.config import TILE_SIZE, TOOLBAR_HEIGHT, TOOLBAR_PAD
from ..core.entities import Direction, QubitState, cw_dir, ccw_dir, DIR_VECTORS
from ..core.world import screen_to_world, get_tile, count_placed, is_locked
from ..engine.gate_registry import get_gate, active_toolbar, Category, EMPTY, OUTPUT_SINK, BELT
from .rendering import (
    get_export_button_rect, get_speed_button_rect, get_pause_button_rect,
    show_toast, toolbar_button_rects, toggle_briefing,
)
from ..core import world as W


def _toolbar_hit(mx, my):
    if my < config.HEIGHT - TOOLBAR_HEIGHT:
        return None
    for rect, gid in toolbar_button_rects(W.available_buildings):
        if rect.collidepoint(mx, my):
            return gid
    return None


def _companion_pos(wx, wy, direction):
    """Compute first companion/control tile position for a multi-qubit gate."""
    cd = ccw_dir(direction)
    dx, dy = DIR_VECTORS[cd]
    return wx + dx, wy + dy


def _multi_cells(wx, wy, tile):
    gate = get_gate(tile.building)
    if not (gate and gate.category == Category.TWO_QUBIT and tile.peer):
        return [(wx, wy)]
    px, py = tile.peer if tile.is_ctrl else (wx, wy)
    primary = get_tile(px, py)
    cd = ccw_dir(primary.direction)
    dx, dy = DIR_VECTORS[cd]
    return [(px + dx * i, py + dy * i) for i in range(gate.qubits)]


def _clear_tile(tile):
    tile.building = EMPTY
    tile.item = None
    tile.spawn_state = None
    tile.spawn_phase = None
    tile.peer = None
    tile.is_ctrl = False
    tile.role = 1


def _clear_linked(wx, wy):
    for cx, cy in _multi_cells(wx, wy, get_tile(wx, wy)):
        _clear_tile(get_tile(cx, cy))


def _can_place_at(wx, wy, available, building):
    """Check if a building can be placed at (wx, wy)."""
    if is_locked((wx, wy)):
        return False
    if available is not None and building not in available:
        return False
    limit = W.gate_limits.get(building)
    if limit is not None and count_placed(building) >= limit:
        return False
    return True


def _place_building(wx, wy, building, direction):
    """Place a building and set up companion cells for multi-qubit gates."""
    tile = get_tile(wx, wy)
    if tile.peer:
        _clear_linked(wx, wy)

    tile = get_tile(wx, wy)
    tile.building = building
    tile.direction = direction
    tile.process_timer = 0.0
    tile.measurements = []
    tile.spawn_state = None
    tile.spawn_phase = None
    tile.peer = None
    tile.is_ctrl = False
    tile.role = 1
    if building == OUTPUT_SINK:
        tile.sink_total = 0
        tile.sink_match = 0
        tile.sink_target = None
        tile.sink_phase = None

    gate = get_gate(building)
    if gate and gate.category == Category.TWO_QUBIT:
        cd = ccw_dir(direction)
        dx, dy = DIR_VECTORS[cd]
        for role in range(2, gate.qubits + 1):
            cx, cy = wx + dx * (role - 1), wy + dy * (role - 1)
            companion = get_tile(cx, cy)
            if companion.peer:
                _clear_linked(cx, cy)
                companion = get_tile(cx, cy)
            companion.building = building
            companion.direction = direction
            companion.item = None
            companion.process_timer = 0.0
            companion.peer = (wx, wy)
            companion.is_ctrl = True
            companion.role = role
        tile.peer = _companion_pos(wx, wy, direction)


def _delete_building(wx, wy):
    """Delete a building and its companion if linked."""
    tile = get_tile(wx, wy)
    if tile.peer:
        for pos in _multi_cells(wx, wy, tile):
            if pos in W.locked_tiles:
                W.locked_tiles.discard(pos)
            _clear_tile(get_tile(*pos))
        return
    _clear_tile(tile)


_SINK_CYCLE = [None, QubitState.ZERO, QubitState.ONE, QubitState.SUPERPOSITION]

# Belt drag state
_drag_active = False
_drag_last_cell = None
_erase_active = False
_erase_last_cell = None


def handle_input(dt, selected_building, selected_rotation, paused, step_requested,
                 events=None):
    global _drag_active, _drag_last_cell, _erase_active, _erase_last_cell

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

    active = active_toolbar(W.available_buildings)
    key_map = {
        kc: gid
        for idx, gid in enumerate(active)
        if (kc := getattr(pygame, f"K_{idx + 1}", None))
    }

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
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_q:
                config.SPEED_MULT = {0.5: 0.5, 1: 0.5, 2: 1, 4: 2}[config.SPEED_MULT]
            elif event.key == pygame.K_e:
                config.SPEED_MULT = {0.5: 1, 1: 2, 2: 4, 4: 4}[config.SPEED_MULT]
            elif event.key == pygame.K_c:
                for pos in list(W.world.keys()):
                    if not is_locked(pos):
                        tile = get_tile(*pos)
                        tile.peer = None
                        tile.is_ctrl = False
                        tile.role = 1
                        del W.world[pos]
            elif event.key == pygame.K_f:
                toggle_briefing()
            elif event.key == pygame.K_x:
                ldef = W._state.current_level_def
                cx, cy = (ldef or {}).get("camera", (0, 0))
                W._state.camera_x = cx * TILE_SIZE - config.WIDTH / 2
                W._state.camera_y = cy * TILE_SIZE - (config.HEIGHT - TOOLBAR_HEIGHT) / 2
                W._state.zoom = 1.0
            elif event.key == pygame.K_TAB:
                back_to_menu = True

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            old_zoom = W._state.zoom
            W._state.zoom = max(0.3, min(3.0, W._state.zoom + event.y * 0.12))
            factor = W._state.zoom / old_zoom
            W._state.camera_x = (mx + W._state.camera_x) * factor - mx
            W._state.camera_y = (my + W._state.camera_y) * factor - my

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if event.button == 1 and get_speed_button_rect().collidepoint(mx, my):
                config.SPEED_MULT = {0.5: 1, 1: 2, 2: 4, 4: 0.5}[config.SPEED_MULT]
                continue

            if event.button == 1 and get_pause_button_rect().collidepoint(mx, my):
                paused = not paused
                continue


            if event.button == 1 and get_export_button_rect().collidepoint(mx, my):
                try:
                    from ..engine.circuit_export import export_circuit
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
                cell_locked = is_locked((wx, wy))

                if event.button == 1 and not cell_locked:
                    if _can_place_at(wx, wy, W.available_buildings, selected_building):
                        gate = get_gate(selected_building)
                        if gate and gate.category == Category.TWO_QUBIT:
                            cdx, cdy = DIR_VECTORS[ccw_dir(selected_rotation)]
                            cells = [
                                (wx + cdx * i, wy + cdy * i)
                                for i in range(1, gate.qubits)
                            ]
                            if any(not _can_place_at(cx, cy, W.available_buildings, selected_building)
                                   for cx, cy in cells):
                                continue
                            for cx, cy in cells:
                                if get_tile(cx, cy).peer:
                                    _delete_building(cx, cy)
                        _place_building(wx, wy, selected_building, selected_rotation)

                        # Start belt drag
                        if selected_building == BELT:
                            _drag_active = True
                            _drag_last_cell = (wx, wy)

                elif event.button == 3:
                    _erase_active = True
                    _erase_last_cell = (wx, wy)
                    if not cell_locked:
                        _delete_building(wx, wy)

                elif event.button == 2:
                    tile = get_tile(wx, wy)
                    if tile.building == OUTPUT_SINK and not cell_locked:
                        idx = _SINK_CYCLE.index(tile.sink_target) if tile.sink_target in _SINK_CYCLE else 0
                        tile.sink_target = _SINK_CYCLE[(idx + 1) % len(_SINK_CYCLE)]
                        tile.sink_phase = None
                        tile.sink_total = 0
                        tile.sink_match = 0

        # Belt drag: place belts as mouse moves
        if event.type == pygame.MOUSEMOTION and _drag_active:
            mx, my = event.pos
            if my < config.HEIGHT - TOOLBAR_HEIGHT:
                wx, wy = screen_to_world(mx, my, TILE_SIZE)
                if (wx, wy) != _drag_last_cell and not is_locked((wx, wy)):
                    lx, ly = _drag_last_cell
                    dx, dy = wx - lx, wy - ly
                    if abs(dx) >= abs(dy):
                        d = Direction.RIGHT if dx > 0 else Direction.LEFT
                    else:
                        d = Direction.DOWN if dy > 0 else Direction.UP
                    # Update previous belt to point toward new cell
                    prev = get_tile(lx, ly)
                    if prev.building == BELT and not is_locked((lx, ly)):
                        prev.direction = d
                    # Place new belt (skip tiles that are part of a multi-qubit gate)
                    target = get_tile(wx, wy)
                    if _can_place_at(wx, wy, W.available_buildings, BELT) and not target.peer:
                        target.building = BELT
                        target.direction = d
                    _drag_last_cell = (wx, wy)

        if event.type == pygame.MOUSEMOTION and _erase_active:
            mx, my = event.pos
            if my < config.HEIGHT - TOOLBAR_HEIGHT:
                wx, wy = screen_to_world(mx, my, TILE_SIZE)
                if (wx, wy) != _erase_last_cell:
                    _erase_last_cell = (wx, wy)
                    if not is_locked((wx, wy)):
                        _delete_building(wx, wy)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            _drag_active = False
            _drag_last_cell = None
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            _erase_active = False
            _erase_last_cell = None

    if active and selected_building not in active:
        selected_building = active[0]

    return True, selected_building, selected_rotation, paused, step_requested, back_to_menu
