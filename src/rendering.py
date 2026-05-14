"""Rendering: grid, buildings, qubits, toolbar, HUD, and level overlays."""

import pygame
import world as world_module
import config

from config import (
    TILE_SIZE, BG, GRID_COLOR, GRID_ORIGIN,
    WHITE, LIGHT_GRAY, DARK_GRAY, YELLOW, RED, GREEN, BLUE,
    TOOLBAR_HEIGHT, TOOLBAR_PAD, TOOLTIP_FONT_SIZE, UI_FONT_SIZE,
    BELT_COLOR, GENERATOR_COLOR, HADAMARD_COLOR, X_GATE_COLOR,
    Z_GATE_COLOR, CNOT_COLOR, MEASUREMENT_COLOR, SPLITTER_COLOR,
    SINK_COLOR, GOLD, PURPLE, CYAN,
)
from entities import (
    BuildingType, QubitState, Direction, DIR_VECTORS,
    state_color, BUILDING_INFO, TOOLBAR_ORDER,
)
from sprites import get_building_sprite
from world import world, get_tile, world_to_screen, screen_to_world


# Building accent colors for toolbar icons
_ACCENT = {
    BuildingType.BELT: BELT_COLOR,
    BuildingType.GENERATOR: GENERATOR_COLOR,
    BuildingType.HADAMARD: HADAMARD_COLOR,
    BuildingType.X_GATE: X_GATE_COLOR,
    BuildingType.Z_GATE: Z_GATE_COLOR,
    BuildingType.CNOT: CNOT_COLOR,
    BuildingType.MEASUREMENT: MEASUREMENT_COLOR,
    BuildingType.SPLITTER: SPLITTER_COLOR,
    BuildingType.OUTPUT_SINK: SINK_COLOR,
}


def _active_toolbar():
    """Return the toolbar buildings available in the current mode."""
    if world_module.available_buildings is not None:
        return [b for b in TOOLBAR_ORDER if b in world_module.available_buildings]
    return list(TOOLBAR_ORDER)


# ---------------------------------------------------------------------------
# Measurement histogram
# ---------------------------------------------------------------------------

def _draw_histogram(surface, rect, tile):
    if not tile.measurements:
        return
    chart = rect.inflate(-14, -22)
    chart.height = max(14, chart.height // 2)
    chart.top = rect.top + 6

    zero_n = sum(1 for o in tile.measurements if o == QubitState.ZERO)
    one_n = sum(1 for o in tile.measurements if o == QubitState.ONE)
    total = max(1, zero_n + one_n)

    gap = 4
    bw = max(3, (chart.width - gap) // 2)
    mh = chart.height - 4

    rh = max(3, int(mh * zero_n / total))
    bh = max(3, int(mh * one_n / total))

    pygame.draw.rect(surface, RED, pygame.Rect(chart.left, chart.bottom - rh, bw, rh))
    pygame.draw.rect(surface, BLUE, pygame.Rect(chart.left + bw + gap, chart.bottom - bh, bw, bh))
    pygame.draw.rect(surface, WHITE, chart, 1)

    ty = chart.bottom + 2
    tw = max(2, chart.width // 20)
    for i, o in enumerate(tile.measurements[-20:]):
        tr = pygame.Rect(chart.left + i * tw, ty, tw - 1, 3)
        pygame.draw.rect(surface, state_color(o), tr)

    if tile.measure_flash > 0:
        alpha = int(160 * min(tile.measure_flash / 0.35, 1.0))
        fs = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fs, (255, 255, 255, alpha), fs.get_rect(), 3, border_radius=6)
        surface.blit(fs, rect.topleft)


# ---------------------------------------------------------------------------
# Output sink overlay
# ---------------------------------------------------------------------------

def _draw_sink_status(surface, rect, tile):
    font = pygame.font.SysFont("consolas", max(10, int(rect.height * 0.18)))

    # Show target color indicator
    if tile.sink_target is not None:
        indicator_color = state_color(tile.sink_target)
        ir = max(4, int(rect.height * 0.08))
        pygame.draw.circle(surface, indicator_color,
                           (rect.centerx, rect.top + ir + 4), ir)

    if tile.sink_total == 0:
        return

    if tile.sink_target is not None:
        pct = int(100 * tile.sink_match / max(1, tile.sink_total))
        color = GREEN if pct > 80 else (YELLOW if pct > 40 else RED)
        txt = font.render(f"{tile.sink_match}/{tile.sink_total}", True, color)
    else:
        txt = font.render(f"#{tile.sink_total}", True, WHITE)
    surface.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 10)))


# ---------------------------------------------------------------------------
# Locked tile overlay
# ---------------------------------------------------------------------------

def _draw_locked_indicator(surface, rect):
    """Small lock icon in corner for pre-placed level tiles."""
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    size = max(8, int(rect.width * 0.18))
    pygame.draw.polygon(s, (255, 255, 255, 30), [
        (rect.width - size, 0), (rect.width, 0), (rect.width, size)
    ])
    surface.blit(s, rect.topleft)


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------

def draw_grid(surface):
    size = TILE_SIZE * world_module.zoom
    playable_h = config.HEIGHT - TOOLBAR_HEIGHT

    sx_start = int(world_module.camera_x // size)
    sx_end = int((world_module.camera_x + config.WIDTH) // size) + 2
    sy_start = int(world_module.camera_y // size)
    sy_end = int((world_module.camera_y + playable_h) // size) + 2

    for wx in range(sx_start, sx_end):
        for wy in range(sy_start, sy_end):
            sx, sy = world_to_screen(wx, wy, TILE_SIZE)
            rect = pygame.Rect(sx, sy, size, size)

            if sy >= playable_h:
                continue

            line_color = GRID_ORIGIN if (wx == 0 or wy == 0) else GRID_COLOR
            pygame.draw.rect(surface, line_color, rect, 1)

            tile = get_tile(wx, wy)

            if tile.building != BuildingType.EMPTY:
                sprite = get_building_sprite(tile.building, tile.direction, int(size))
                if sprite:
                    surface.blit(sprite, sprite.get_rect(center=rect.center))

                if tile.building == BuildingType.MEASUREMENT:
                    _draw_histogram(surface, rect, tile)
                elif tile.building == BuildingType.OUTPUT_SINK:
                    _draw_sink_status(surface, rect, tile)

                if (wx, wy) in world_module.locked_tiles:
                    _draw_locked_indicator(surface, rect)

            if tile.item:
                _draw_item_on_tile(surface, tile, tile.item, sx, sy, size)

            if tile.control_item:
                _draw_item_on_tile(surface, tile, tile.control_item, sx, sy, size,
                                   control=True)


def _draw_item_on_tile(surface, tile, item, sx, sy, size, control=False):
    dx, dy = DIR_VECTORS[tile.direction]
    if tile.building == BuildingType.GENERATOR:
        px, py = sx + size / 2, sy + size / 2
    elif control:
        from entities import ccw_dir
        cd = ccw_dir(tile.direction)
        cdx, cdy = DIR_VECTORS[cd]
        px = sx + size / 2 + cdx * size * 0.2
        py = sy + size / 2 + cdy * size * 0.2
    else:
        px = sx + size / 2 + dx * item.progress * size * 0.4
        py = sy + size / 2 + dy * item.progress * size * 0.4
    item.draw(surface, px - 10, py - 10, 20)


# ---------------------------------------------------------------------------
# Ghost preview
# ---------------------------------------------------------------------------

def draw_ghost(surface, selected_building, selected_rotation, mouse_pos):
    if selected_building == BuildingType.EMPTY:
        return
    mx, my = mouse_pos
    if my >= config.HEIGHT - TOOLBAR_HEIGHT:
        return

    wx, wy = screen_to_world(mx, my, TILE_SIZE)

    if (wx, wy) in world_module.locked_tiles:
        return

    sx, sy = world_to_screen(wx, wy, TILE_SIZE)
    size = int(TILE_SIZE * world_module.zoom)

    sprite = get_building_sprite(selected_building, selected_rotation, size)
    if sprite:
        ghost = sprite.copy()
        ghost.set_alpha(90)
        surface.blit(ghost, ghost.get_rect(center=(sx + size // 2, sy + size // 2)))


# ---------------------------------------------------------------------------
# Toolbar
# ---------------------------------------------------------------------------

def draw_toolbar(surface, selected_building, selected_rotation, paused):
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    pygame.draw.rect(surface, (22, 22, 28), (0, tb_y, config.WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(surface, DARK_GRAY, (0, tb_y), (config.WIDTH, tb_y), 1)

    font = pygame.font.SysFont("consolas", UI_FONT_SIZE)
    small = pygame.font.SysFont("consolas", TOOLTIP_FONT_SIZE)

    active = _active_toolbar()
    btn_size = TOOLBAR_HEIGHT - 2 * TOOLBAR_PAD
    total = len(active)
    start_x = max(TOOLBAR_PAD, (config.WIDTH - total * (btn_size + TOOLBAR_PAD)) // 2)

    for i, bt in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)

        accent = _ACCENT.get(bt, WHITE)
        is_sel = bt == selected_building

        if is_sel:
            pygame.draw.rect(surface, (*accent[:3], 40), rect, border_radius=8)
            pygame.draw.rect(surface, accent, rect, 2, border_radius=8)
        else:
            pygame.draw.rect(surface, (35, 35, 42), rect, border_radius=8)
            pygame.draw.rect(surface, DARK_GRAY, rect, 1, border_radius=8)

        mini = get_building_sprite(bt, Direction.RIGHT, btn_size - 8)
        if mini:
            surface.blit(mini, mini.get_rect(center=rect.center))

        key_label = str(i + 1)
        key_txt = small.render(key_label, True, accent if is_sel else LIGHT_GRAY)
        surface.blit(key_txt, (bx + 3, by + 2))

    # Status (right side)
    rx = config.WIDTH - 10
    status_txt = "PAUSED" if paused else "RUNNING"
    status_col = RED if paused else GREEN
    st = font.render(status_txt, True, status_col)
    surface.blit(st, st.get_rect(topright=(rx, tb_y + 8)))

    rot_txt = font.render(f"Dir: {selected_rotation.name}", True, LIGHT_GRAY)
    surface.blit(rot_txt, rot_txt.get_rect(topright=(rx, tb_y + 28)))

    controls = "R Rotate | P Pause | N Step | WASD Pan | Scroll Zoom | ESC Menu"
    ctrl_txt = small.render(controls, True, DARK_GRAY)
    surface.blit(ctrl_txt, ctrl_txt.get_rect(topright=(rx, tb_y + 48)))


# ---------------------------------------------------------------------------
# Tooltip
# ---------------------------------------------------------------------------

def draw_tooltip(surface, mouse_pos, selected_building):
    mx, my = mouse_pos
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    if my < tb_y:
        return

    active = _active_toolbar()
    btn_size = TOOLBAR_HEIGHT - 2 * TOOLBAR_PAD
    total = len(active)
    start_x = max(TOOLBAR_PAD, (config.WIDTH - total * (btn_size + TOOLBAR_PAD)) // 2)

    for i, bt in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)
        if rect.collidepoint(mx, my):
            info = BUILDING_INFO[bt]
            font = pygame.font.SysFont("consolas", TOOLTIP_FONT_SIZE)
            tip = font.render(f"{info['name']}: {info['tip']}", True, WHITE)
            tip_rect = tip.get_rect(midbottom=(rect.centerx, tb_y - 4))
            tip_rect.left = max(4, tip_rect.left)
            tip_rect.right = min(config.WIDTH - 4, tip_rect.right)
            bg = tip_rect.inflate(8, 4)
            pygame.draw.rect(surface, (30, 30, 36), bg, border_radius=4)
            pygame.draw.rect(surface, DARK_GRAY, bg, 1, border_radius=4)
            surface.blit(tip, tip_rect)
            break


# ---------------------------------------------------------------------------
# Level HUD (top bar showing objective and progress)
# ---------------------------------------------------------------------------

def draw_level_hud(surface):
    """Draw level-specific info: name, hint, progress."""
    lev = world_module.current_level_def
    if lev is None:
        return

    idx = world_module.current_level_index
    win_count = lev.get("win_count", 5)

    # Find best progress across sinks
    best = 0
    for (x, y) in world_module.locked_tiles:
        tile = get_tile(x, y)
        if tile.building == BuildingType.OUTPUT_SINK:
            if tile.sink_target is None:
                best = max(best, tile.sink_total)
            else:
                best = max(best, tile.sink_match)

    # Top bar background
    bar_h = 44
    bar = pygame.Surface((config.WIDTH, bar_h), pygame.SRCALPHA)
    bar.fill((10, 10, 14, 200))
    surface.blit(bar, (0, 0))

    font = pygame.font.SysFont("consolas", 16)
    small = pygame.font.SysFont("consolas", 13)

    # Level name (left)
    name_txt = font.render(f"Level {idx + 1}: {lev['name']}", True, CYAN)
    surface.blit(name_txt, (12, 6))

    # Hint (left, below name)
    hint_txt = small.render(lev.get("hint", ""), True, LIGHT_GRAY)
    surface.blit(hint_txt, (12, 26))

    # Progress bar (right)
    bar_w = 160
    bar_h2 = 14
    bx = config.WIDTH - bar_w - 60
    by = 8

    progress = min(1.0, best / max(1, win_count))
    pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h2), border_radius=4)
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        color = GREEN if progress >= 1.0 else CYAN
        pygame.draw.rect(surface, color, (bx, by, fill_w, bar_h2), border_radius=4)
    pygame.draw.rect(surface, LIGHT_GRAY, (bx, by, bar_w, bar_h2), 1, border_radius=4)

    # Count text
    count_txt = font.render(f"{min(best, win_count)}/{win_count}", True, WHITE)
    surface.blit(count_txt, count_txt.get_rect(midleft=(bx + bar_w + 8, by + bar_h2 // 2)))

    # ESC hint
    esc_txt = small.render("ESC = Back to menu", True, DARK_GRAY)
    surface.blit(esc_txt, esc_txt.get_rect(topright=(config.WIDTH - 12, 28)))


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

def draw_hud(surface):
    font = pygame.font.SysFont("consolas", UI_FONT_SIZE)
    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my, TILE_SIZE)
    if world_module.current_level_def is None:
        txt = font.render(f"({wx}, {wy})", True, DARK_GRAY)
        surface.blit(txt, txt.get_rect(topright=(config.WIDTH - 10, 8)))


# ---------------------------------------------------------------------------
# Public draw_ui
# ---------------------------------------------------------------------------

def draw_ui(surface, selected_building, selected_rotation, paused):
    mouse_pos = pygame.mouse.get_pos()
    draw_ghost(surface, selected_building, selected_rotation, mouse_pos)
    draw_toolbar(surface, selected_building, selected_rotation, paused)
    draw_tooltip(surface, mouse_pos, selected_building)
    draw_level_hud(surface)
    draw_hud(surface)
