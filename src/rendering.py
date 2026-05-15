"""Rendering: grid, buildings, qubits, toolbar, HUD, and level overlays."""

import pygame
import world as world_module
import config

from config import (
    TILE_SIZE, BG, GRID_COLOR, GRID_ORIGIN,
    WHITE, LIGHT_GRAY, DARK_GRAY, YELLOW, RED, GREEN, BLUE,
    TOOLBAR_HEIGHT, TOOLBAR_PAD, TOOLTIP_FONT_SIZE, UI_FONT_SIZE,
    GOLD, PURPLE, CYAN,
)
from entities import (
    QubitState, Direction, DIR_VECTORS, state_color,
)
from sprites import get_building_sprite
from world import world, get_tile, world_to_screen, screen_to_world
from gate_registry import (
    get_gate, toolbar_order, Category,
    EMPTY, GENERATOR, OUTPUT_SINK,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active_toolbar():
    """Return gate IDs available in the current mode."""
    all_ids = [g.id for g in toolbar_order()]
    if world_module.available_buildings is not None:
        return [gid for gid in all_ids if gid in world_module.available_buildings]
    return all_ids


# ---------------------------------------------------------------------------
# Output sink overlay
# ---------------------------------------------------------------------------

def _draw_sink_status(surface, rect, tile):
    font = pygame.font.SysFont("consolas", max(10, int(rect.height * 0.18)))
    if tile.sink_target is not None:
        ic = state_color(tile.sink_target)
        ir = max(4, int(rect.height * 0.08))
        pygame.draw.circle(surface, ic, (rect.centerx, rect.top + ir + 4), ir)
    if tile.sink_total == 0:
        return
    if tile.sink_target is not None:
        pct = int(100 * tile.sink_match / max(1, tile.sink_total))
        color = GREEN if pct > 80 else (YELLOW if pct > 40 else RED)
        txt = font.render(f"{tile.sink_match}/{tile.sink_total}", True, color)
    else:
        txt = font.render(f"#{tile.sink_total}", True, WHITE)
    surface.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 10)))


def _draw_locked_indicator(surface, rect):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    sz = max(8, int(rect.width * 0.18))
    pygame.draw.polygon(s, (255, 255, 255, 30), [
        (rect.width - sz, 0), (rect.width, 0), (rect.width, sz)
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

            if tile.building != EMPTY:
                sprite = get_building_sprite(tile.building, tile.direction, int(size))
                if sprite:
                    surface.blit(sprite, sprite.get_rect(center=rect.center))

                # Gate-specific overlay (e.g. measurement histogram)
                gate = get_gate(tile.building)
                if gate and gate.overlay_fn:
                    gate.overlay_fn(surface, rect, tile)

                # Sink status
                if tile.building == OUTPUT_SINK:
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
    if tile.building == GENERATOR:
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
    if selected_building == EMPTY:
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

    for i, gid in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)

        gate = get_gate(gid)
        accent = gate.color if gate else WHITE
        is_sel = gid == selected_building

        if is_sel:
            pygame.draw.rect(surface, (*accent[:3], 40), rect, border_radius=8)
            pygame.draw.rect(surface, accent, rect, 2, border_radius=8)
        else:
            pygame.draw.rect(surface, (35, 35, 42), rect, border_radius=8)
            pygame.draw.rect(surface, DARK_GRAY, rect, 1, border_radius=8)

        mini = get_building_sprite(gid, Direction.RIGHT, btn_size - 8)
        if mini:
            surface.blit(mini, mini.get_rect(center=rect.center))

        key_txt = small.render(str(i + 1), True, accent if is_sel else LIGHT_GRAY)
        surface.blit(key_txt, (bx + 3, by + 2))

    rx = config.WIDTH - 10
    st = font.render("PAUSED" if paused else "RUNNING", True, RED if paused else GREEN)
    surface.blit(st, st.get_rect(topright=(rx, tb_y + 8)))
    rot = font.render(f"Dir: {selected_rotation.name}", True, LIGHT_GRAY)
    surface.blit(rot, rot.get_rect(topright=(rx, tb_y + 28)))
    ctrl = small.render("R Rotate | P Pause | N Step | WASD Pan | Scroll Zoom | ESC Menu", True, DARK_GRAY)
    surface.blit(ctrl, ctrl.get_rect(topright=(rx, tb_y + 48)))


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
    start_x = max(TOOLBAR_PAD, (config.WIDTH - len(active) * (btn_size + TOOLBAR_PAD)) // 2)
    for i, gid in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        rect = pygame.Rect(bx, by, btn_size, btn_size)
        if rect.collidepoint(mx, my):
            gate = get_gate(gid)
            if gate:
                font = pygame.font.SysFont("consolas", TOOLTIP_FONT_SIZE)
                tip = font.render(f"{gate.name}: {gate.tip}", True, WHITE)
                tip_rect = tip.get_rect(midbottom=(rect.centerx, tb_y - 4))
                tip_rect.left = max(4, tip_rect.left)
                tip_rect.right = min(config.WIDTH - 4, tip_rect.right)
                bg = tip_rect.inflate(8, 4)
                pygame.draw.rect(surface, (30, 30, 36), bg, border_radius=4)
                pygame.draw.rect(surface, DARK_GRAY, bg, 1, border_radius=4)
                surface.blit(tip, tip_rect)
            break


# ---------------------------------------------------------------------------
# Level HUD
# ---------------------------------------------------------------------------

def draw_level_hud(surface):
    lev = world_module.current_level_def
    if lev is None:
        return
    idx = world_module.current_level_index
    win_count = lev.get("win_count", 5)
    best = 0
    for (x, y) in world_module.locked_tiles:
        tile = get_tile(x, y)
        if tile.building == OUTPUT_SINK:
            if tile.sink_target is None:
                best = max(best, tile.sink_total)
            else:
                best = max(best, tile.sink_match)
    bar_h = 44
    bar = pygame.Surface((config.WIDTH, bar_h), pygame.SRCALPHA)
    bar.fill((10, 10, 14, 200))
    surface.blit(bar, (0, 0))
    font = pygame.font.SysFont("consolas", 16)
    small = pygame.font.SysFont("consolas", 13)
    surface.blit(font.render(f"Level {idx + 1}: {lev['name']}", True, CYAN), (12, 6))
    surface.blit(small.render(lev.get("hint", ""), True, LIGHT_GRAY), (12, 26))
    bar_w, bar_h2 = 160, 14
    bx = config.WIDTH - bar_w - 60
    by = 8
    progress = min(1.0, best / max(1, win_count))
    pygame.draw.rect(surface, DARK_GRAY, (bx, by, bar_w, bar_h2), border_radius=4)
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        c = GREEN if progress >= 1.0 else CYAN
        pygame.draw.rect(surface, c, (bx, by, fill_w, bar_h2), border_radius=4)
    pygame.draw.rect(surface, LIGHT_GRAY, (bx, by, bar_w, bar_h2), 1, border_radius=4)
    ct = font.render(f"{min(best, win_count)}/{win_count}", True, WHITE)
    surface.blit(ct, ct.get_rect(midleft=(bx + bar_w + 8, by + bar_h2 // 2)))
    et = small.render("ESC = Back to menu", True, DARK_GRAY)
    surface.blit(et, et.get_rect(topright=(config.WIDTH - 12, 28)))


def draw_hud(surface):
    font = pygame.font.SysFont("consolas", UI_FONT_SIZE)
    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my, TILE_SIZE)
    if world_module.current_level_def is None:
        txt = font.render(f"({wx}, {wy})", True, DARK_GRAY)
        surface.blit(txt, txt.get_rect(topright=(config.WIDTH - 10, 8)))


def draw_ui(surface, selected_building, selected_rotation, paused):
    mouse_pos = pygame.mouse.get_pos()
    draw_ghost(surface, selected_building, selected_rotation, mouse_pos)
    draw_toolbar(surface, selected_building, selected_rotation, paused)
    draw_tooltip(surface, mouse_pos, selected_building)
    draw_level_hud(surface)
    draw_hud(surface)
