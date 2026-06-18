"""Rendering: grid, buildings, qubits, toolbar, HUD, and level overlays."""

from __future__ import annotations

import pygame
from ..core import world as world_module
from ..core import config
from ..core.config import (
    TILE_SIZE, BG, GRID_COLOR,
    WHITE, LIGHT_GRAY, DARK_GRAY, RED, GREEN, BLUE,
    TOOLBAR_HEIGHT, TOOLBAR_PAD, TOOLTIP_FONT_SIZE, UI_FONT_SIZE,
    GOLD, PURPLE, CYAN,
)
from ..core.entities import (
    QubitItem, Direction, DIR_VECTORS, ccw_dir,
)
from .sprites import get_building_sprite, get_qubit_sprite
from ..core.world import get_tile, world_to_screen, screen_to_world, count_placed
from ..engine.gate_registry import (
    get_gate, active_toolbar, Category,
    EMPTY, GENERATOR, OUTPUT_SINK,
)


def toolbar_button_rects(available=None):
    """Yield (rect, gate_id) for each toolbar button."""
    active = active_toolbar(available)
    btn_size = TOOLBAR_HEIGHT - 2 * TOOLBAR_PAD
    start_x = max(TOOLBAR_PAD, (config.WIDTH - len(active) * (btn_size + TOOLBAR_PAD)) // 2)
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    for i, gid in enumerate(active):
        bx = start_x + i * (btn_size + TOOLBAR_PAD)
        by = tb_y + TOOLBAR_PAD
        yield pygame.Rect(bx, by, btn_size, btn_size), gid


def _draw_sink_status(surface, rect, tile):
    lev = world_module.current_level_def
    if tile.sink_target is not None:
        sz = max(20, int(rect.height * 0.35))
        sprite = get_qubit_sprite(
            tile.sink_target, sz, phase_angle=tile.sink_phase or 0.0)
        surface.blit(sprite,
                     sprite.get_rect(center=(rect.centerx, rect.top + sz // 2 + 4)))
    if lev is None:
        return
    win_count = lev.get("win_count", 5)
    match = tile.sink_match if tile.sink_target is not None else tile.sink_total
    color = GREEN if match >= win_count else (CYAN if match > 0 else LIGHT_GRAY)
    font = pygame.font.SysFont("consolas", max(10, int(rect.height * 0.18)))
    txt = font.render(f"{min(match, win_count)}/{win_count}", True, color)
    surface.blit(txt, txt.get_rect(center=(rect.centerx, rect.bottom - 10)))


def _draw_locked_indicator(surface, rect):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    sz = max(8, int(rect.width * 0.18))
    pygame.draw.polygon(s, (255, 255, 255, 30), [
        (rect.width - sz, 0), (rect.width, 0), (rect.width, sz)
    ])
    surface.blit(s, rect.topleft)


def _draw_peer_link(surface, rect, tile, size):
    """Draw a connecting line between primary and companion tiles."""
    if tile.peer is None or tile.is_ctrl:
        return
    cx, cy = tile.peer
    px, py = rect.centerx, rect.centery
    csx, csy = world_to_screen(cx, cy, TILE_SIZE)
    csx += size // 2
    csy += size // 2
    gate = get_gate(tile.building)
    color = gate.color if gate else LIGHT_GRAY
    roles = (gate.qubits if gate else 2) - 1
    end = (px + (csx - px) * roles, py + (csy - py) * roles)
    pygame.draw.line(surface, color, (px, py), end, max(2, int(size * 0.04)))


def draw_grid(surface):
    size = TILE_SIZE * world_module._state.zoom
    playable_h = config.HEIGHT - TOOLBAR_HEIGHT
    sx_start = int(world_module._state.camera_x // size)
    sx_end = int((world_module._state.camera_x + config.WIDTH) // size) + 2
    sy_start = int(world_module._state.camera_y // size)
    sy_end = int((world_module._state.camera_y + playable_h) // size) + 2

    for wx in range(sx_start, sx_end):
        for wy in range(sy_start, sy_end):
            sx, sy = world_to_screen(wx, wy, TILE_SIZE)
            rect = pygame.Rect(sx, sy, size, size)
            if sy >= playable_h:
                continue
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

            tile = get_tile(wx, wy)

            if tile.building != EMPTY:
                role = getattr(tile, "role", 1)
                if tile.is_ctrl and role == 1:
                    role = 2
                sprite = get_building_sprite(
                    tile.building, tile.direction, int(size), role=role)
                if sprite:
                    surface.blit(sprite, sprite.get_rect(center=rect.center))

                _draw_peer_link(surface, rect, tile, int(size))

                gate = get_gate(tile.building)
                if gate and gate.overlay_fn:
                    gate.overlay_fn(surface, rect, tile)

                if tile.building == OUTPUT_SINK:
                    _draw_sink_status(surface, rect, tile)

                if (wx, wy) in world_module.locked_tiles:
                    _draw_locked_indicator(surface, rect)

            if tile.item:
                _draw_item_on_tile(surface, tile, tile.item, sx, sy, size)


def draw_qubit_item(surface, item: QubitItem, x, y, size):
    if item.is_disappearing:
        scale = max(0.18, item.disappear_time / 0.3)
    else:
        scale = 1.0
    sprite_size = max(8, int(size * scale))
    sprite = get_qubit_sprite(item.state, sprite_size,
                              item.is_disappearing, scale,
                              item.entangle_group is not None,
                              item.phase_flipped, item.phase_angle, item.bloch)
    sprite_rect = sprite.get_rect(center=(x + size // 2, y + size // 2))
    surface.blit(sprite, sprite_rect)


def _draw_item_on_tile(surface, tile, item, sx, sy, size):
    dx, dy = DIR_VECTORS[tile.direction]
    if tile.building == GENERATOR:
        px, py = sx + size / 2, sy + size / 2
    else:
        px = sx + size / 2 + dx * item.progress * size * 0.4
        py = sy + size / 2 + dy * item.progress * size * 0.4
    q = max(20, int(size * 0.45))
    draw_qubit_item(surface, item, px - q // 2, py - q // 2, q)


def _companion_offset(direction):
    """Return (dx, dy) for companion tile position — CCW from gate direction."""
    cd = ccw_dir(direction)
    return DIR_VECTORS[cd]


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
    size = int(TILE_SIZE * world_module._state.zoom)
    sprite = get_building_sprite(selected_building, selected_rotation, size)
    if sprite:
        ghost = sprite.copy()
        ghost.set_alpha(90)
        surface.blit(ghost, ghost.get_rect(center=(sx + size // 2, sy + size // 2)))

    # Show companion ghosts for multi-qubit gates
    gate = get_gate(selected_building)
    if gate and gate.category == Category.TWO_QUBIT:
        cdx, cdy = _companion_offset(selected_rotation)
        for role in range(2, gate.qubits + 1):
            cw, ch = wx + cdx * (role - 1), wy + cdy * (role - 1)
            csx, csy = world_to_screen(cw, ch, TILE_SIZE)
            ctrl_sprite = get_building_sprite(selected_building, selected_rotation, size, role=role)
            if ctrl_sprite:
                ctrl_ghost = ctrl_sprite.copy()
                blocked = (cw, ch) in world_module.locked_tiles
                ctrl_ghost.set_alpha(40 if blocked else 90)
                surface.blit(ctrl_ghost, ctrl_ghost.get_rect(
                    center=(csx + size // 2, csy + size // 2)))


def _draw_help_tooltip(surface, anchor_rect):
    font = pygame.font.SysFont("consolas", 13)
    lines = [
        "R  Rotate direction",
        "SPACE  Pause / Resume",
        "Q / E  Slow / Fast",
        "N  Single step",
        "C  Clear all placed",
        "O  Recenter camera",
        "WASD  Pan camera",
        "Scroll  Zoom",
        "ESC  Back to menu",
    ]
    if world_module.current_level_index is not None:
        lines.insert(3, "H  Show briefing")
    rendered = [font.render(l, True, WHITE) for l in lines]
    lh = font.get_linesize()
    pad = 10
    w = max(r.get_width() for r in rendered) + pad * 2
    h = lh * len(rendered) + pad * 2
    box = pygame.Rect(anchor_rect.right - w, anchor_rect.top - h - 6, w, h)
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    bg.fill((20, 18, 30, 240))
    surface.blit(bg, box.topleft)
    pygame.draw.rect(surface, CYAN, box, 1, border_radius=6)
    for i, r in enumerate(rendered):
        surface.blit(r, (box.left + pad, box.top + pad + i * lh))


def draw_toolbar(surface, selected_building, selected_rotation, paused):
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    pygame.draw.rect(surface, (22, 22, 28), (0, tb_y, config.WIDTH, TOOLBAR_HEIGHT))
    pygame.draw.line(surface, DARK_GRAY, (0, tb_y), (config.WIDTH, tb_y), 1)

    font = pygame.font.SysFont("consolas", UI_FONT_SIZE)
    small = pygame.font.SysFont("consolas", TOOLTIP_FONT_SIZE)

    for i, (rect, gid) in enumerate(toolbar_button_rects(world_module.available_buildings)):
        gate = get_gate(gid)
        accent = gate.color if gate else WHITE
        is_sel = gid == selected_building

        if is_sel:
            pygame.draw.rect(surface, (*accent[:3], 40), rect, border_radius=8)
            pygame.draw.rect(surface, accent, rect, 2, border_radius=8)
        else:
            pygame.draw.rect(surface, (35, 35, 42), rect, border_radius=8)
            pygame.draw.rect(surface, DARK_GRAY, rect, 1, border_radius=8)

        btn_size = rect.width
        mini = get_building_sprite(gid, Direction.RIGHT, btn_size - 8)
        if mini:
            surface.blit(mini, mini.get_rect(center=rect.center))

        limit = world_module.gate_limits.get(gid)
        if limit is not None:
            remaining = max(0, limit - count_placed(gid))
            badge_font = pygame.font.SysFont("consolas", max(10, int(btn_size * 0.3)), bold=True)
            badge_color = WHITE if remaining > 0 else RED
            badge = badge_font.render(str(remaining), True, badge_color)
            surface.blit(badge, badge.get_rect(topright=(rect.right - 2, rect.top + 2)))

    export_font = pygame.font.SysFont("consolas", 13, bold=True)
    export_rect = get_export_button_rect()
    mx, my = pygame.mouse.get_pos()
    export_hover = export_rect.collidepoint(mx, my)
    bg_col = (60, 40, 100) if export_hover else (40, 30, 60)
    pygame.draw.rect(surface, bg_col, export_rect, border_radius=6)
    pygame.draw.rect(surface, PURPLE if export_hover else (80, 60, 120),
                     export_rect, 1, border_radius=6)
    et = export_font.render("Export", True, WHITE if export_hover else LIGHT_GRAY)
    surface.blit(et, et.get_rect(center=export_rect.center))

    def _draw_ctrl_btn(rect, label, color, hover):
        bg = (60, 40, 100) if hover else (40, 30, 60)
        pygame.draw.rect(surface, bg, rect, border_radius=6)
        pygame.draw.rect(surface, color if hover else (80, 60, 120), rect, 1, border_radius=6)
        t = small.render(label, True, WHITE if hover else LIGHT_GRAY)
        surface.blit(t, t.get_rect(center=rect.center))

    speed_rect = get_speed_button_rect()
    _draw_ctrl_btn(speed_rect, f"{config.SPEED_MULT}x", CYAN, speed_rect.collidepoint(mx, my))

    pause_rect = get_pause_button_rect()
    p_label = "| |" if not paused else ">"
    p_color = RED if paused else GREEN
    _draw_ctrl_btn(pause_rect, p_label, p_color, pause_rect.collidepoint(mx, my))

    help_rect = get_help_button_rect()
    help_hover = help_rect.collidepoint(mx, my)
    _draw_ctrl_btn(help_rect, "?", CYAN, help_hover)

    if help_hover:
        _draw_help_tooltip(surface, help_rect)



def draw_tooltip(surface, mouse_pos, selected_building):
    mx, my = mouse_pos
    if my < config.HEIGHT - TOOLBAR_HEIGHT:
        return
    for rect, gid in toolbar_button_rects(world_module.available_buildings):
        if rect.collidepoint(mx, my):
            gate = get_gate(gid)
            if gate:
                font = pygame.font.SysFont("consolas", TOOLTIP_FONT_SIZE)
                tip = font.render(f"{gate.name}: {gate.tip}", True, WHITE)
                tb_y = config.HEIGHT - TOOLBAR_HEIGHT
                tip_rect = tip.get_rect(midbottom=(rect.centerx, tb_y - 4))
                tip_rect.left = max(4, tip_rect.left)
                tip_rect.right = min(config.WIDTH - 4, tip_rect.right)
                bg = tip_rect.inflate(8, 4)
                pygame.draw.rect(surface, (30, 30, 36), bg, border_radius=4)
                pygame.draw.rect(surface, DARK_GRAY, bg, 1, border_radius=4)
                surface.blit(tip, tip_rect)
            break


def draw_level_hud(surface):
    lev = world_module.current_level_def
    if lev is None:
        return
    idx = world_module.current_level_index
    win_count = lev.get("win_count", 5)
    if lev.get("win_type") == "measure":
        best = sum(len(t.measurements) for t in world_module.world.values()
                   if t.building == "measurement")
    else:
        sink_counts = []
        for (x, y) in world_module.locked_tiles:
            tile = get_tile(x, y)
            if tile.building == OUTPUT_SINK:
                c = tile.sink_total if tile.sink_target is None else tile.sink_match
                sink_counts.append(c)
        best = min(sink_counts) if sink_counts else 0
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


def _draw_compass(surface, direction, cx, cy):
    import math
    r = 20
    pygame.draw.circle(surface, (30, 30, 38), (cx, cy), r)
    pygame.draw.circle(surface, DARK_GRAY, (cx, cy), r, 1)
    angles = {Direction.RIGHT: 0, Direction.UP: -90, Direction.LEFT: 180, Direction.DOWN: 90}
    angle = math.radians(angles[direction])
    ex = cx + int(r * 0.7 * math.cos(angle))
    ey = cy + int(r * 0.7 * math.sin(angle))
    pygame.draw.line(surface, CYAN, (cx, cy), (ex, ey), 2)
    pygame.draw.circle(surface, CYAN, (ex, ey), 3)
    font = pygame.font.SysFont("consolas", 10)
    label = font.render(direction.name[0], True, CYAN)
    surface.blit(label, label.get_rect(center=(cx, cy + r + 10)))


def draw_hud(surface, selected_rotation):
    font = pygame.font.SysFont("consolas", UI_FONT_SIZE)
    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my, TILE_SIZE)
    coord = font.render(f"({wx}, {wy})", True, DARK_GRAY)
    compass_cy = 78
    compass_r = 20
    compass_cx = config.WIDTH - 30 - compass_r
    _draw_compass(surface, selected_rotation, compass_cx, compass_cy)
    coord_rect = coord.get_rect(midtop=(compass_cx, compass_cy + compass_r + 20))
    surface.blit(coord, coord_rect)


_toast_text: str = ""
_toast_timer: float = 0.0


def show_toast(message: str, duration: float = 3.0):
    global _toast_text, _toast_timer
    _toast_text = message
    _toast_timer = duration


def tick_toast(dt: float):
    global _toast_timer
    if _toast_timer > 0:
        _toast_timer = max(0.0, _toast_timer - dt)


def _draw_toast(surface):
    if _toast_timer <= 0:
        return
    font = pygame.font.SysFont("consolas", 15)
    txt = font.render(_toast_text, True, WHITE)
    padding = 12
    tw, th = txt.get_size()
    box = pygame.Rect(0, 0, tw + padding * 2, th + padding)
    box.midtop = (config.WIDTH // 2, 60)
    alpha = min(1.0, _toast_timer / 0.5) * 220
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    bg.fill((30, 20, 50, int(alpha)))
    surface.blit(bg, box.topleft)
    pygame.draw.rect(surface, (*PURPLE[:3], int(alpha)), box, 1, border_radius=6)
    txt.set_alpha(int(alpha))
    surface.blit(txt, txt.get_rect(center=box.center))


_show_briefing = False


def toggle_briefing():
    global _show_briefing
    _show_briefing = not _show_briefing


def reset_briefing():
    global _show_briefing
    _show_briefing = False


def draw_briefing_overlay(surface, hint="Press H to close", force=False):
    if not force and not _show_briefing:
        return
    lev = world_module.current_level_def
    if lev is None:
        return
    text = lev.get("briefing", "")
    if not text:
        return
    font = pygame.font.SysFont("consolas", 15)
    lines = text.split("\n")
    rendered = [font.render(line, True, WHITE) for line in lines]
    line_h = font.get_linesize()
    pad = 20
    w = max(r.get_width() for r in rendered) + pad * 2
    h = line_h * len(rendered) + pad * 2
    box = pygame.Rect(0, 0, w, h)
    box.center = (config.WIDTH // 2, (config.HEIGHT - TOOLBAR_HEIGHT) // 2)
    bg = pygame.Surface(box.size, pygame.SRCALPHA)
    bg.fill((15, 12, 25, 230))
    surface.blit(bg, box.topleft)
    pygame.draw.rect(surface, CYAN, box, 1, border_radius=8)
    for i, r in enumerate(rendered):
        surface.blit(r, (box.left + pad, box.top + pad + i * line_h))
    hint_txt = font.render(hint, True, DARK_GRAY)
    surface.blit(hint_txt, hint_txt.get_rect(midtop=(box.centerx, box.bottom + 4)))


def get_export_button_rect():
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    export_w, export_h = 80, 26
    return pygame.Rect(config.WIDTH - export_w - 46, tb_y + 6, export_w, export_h)


def get_speed_button_rect():
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    return pygame.Rect(12, tb_y + 6, 50, 26)


def get_pause_button_rect():
    tb_y = config.HEIGHT - TOOLBAR_HEIGHT
    return pygame.Rect(68, tb_y + 6, 50, 26)


def get_help_button_rect():
    r = get_export_button_rect()
    return pygame.Rect(r.right + 6, r.top, 26, r.height)


def draw_ui(surface, selected_building, selected_rotation, paused):
    mouse_pos = pygame.mouse.get_pos()
    draw_ghost(surface, selected_building, selected_rotation, mouse_pos)
    draw_toolbar(surface, selected_building, selected_rotation, paused)
    draw_tooltip(surface, mouse_pos, selected_building)
    draw_level_hud(surface)
    draw_hud(surface, selected_rotation)
    draw_briefing_overlay(surface)
    _draw_toast(surface)
