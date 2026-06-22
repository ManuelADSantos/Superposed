"""Menu screens: main menu, campaign select, level briefing overlay, and win screen."""

from __future__ import annotations

import random
import pygame
from enum import Enum

from ..core import config
from ..core.config import (
    WHITE, LIGHT_GRAY, DARK_GRAY, GREEN,
    RED, BLUE, PURPLE, CYAN, GOLD,
)
from ..content.levels import CHAPTERS, ALL_LEVELS, chapter_level_offset


# ── Background particles ──
_PARTICLE_COLORS = [(220, 80, 80), (100, 160, 255), (170, 90, 255)]
_particles: list[list] = []  # [x, y, vx, vy, radius, color_idx]
_last_size = (0, 0)


def _draw_particles(screen):
    global _last_size
    w, h = config.WIDTH, config.HEIGHT
    n = 400
    if not _particles or (w, h) != _last_size:
        _particles.clear()
        for _ in range(n):
            _particles.append([
                random.uniform(0, w), random.uniform(0, h),
                random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4),
                random.randint(3, 7), random.randint(0, 2),
            ])
        _last_size = (w, h)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for p in _particles:
        p[0] += p[2]
        p[1] += p[3]
        if p[0] < 0 or p[0] > w:
            p[2] = -p[2]
            p[0] = max(0, min(w, p[0]))
        if p[1] < 0 or p[1] > h:
            p[3] = -p[3]
            p[1] = max(0, min(h, p[1]))
        r, g, b = _PARTICLE_COLORS[p[5]]
        pygame.draw.circle(surf, (r, g, b, 30), (int(p[0]), int(p[1])), int(p[4]))
    screen.blit(surf, (0, 0))


class GameState(Enum):
    MAIN_MENU = 0
    CHAPTER_SELECT = 1
    LEVEL_SELECT = 2
    SANDBOX = 3
    LEVEL_PLAY = 4
    WIN_SCREEN = 5


_BG_MENU = (10, 10, 14)
_PANEL = (24, 24, 30)
_PANEL_HOVER = (34, 34, 44)
_PANEL_BORDER = (55, 55, 70)
_ACCENT = PURPLE
_ACCENT_DIM = (120, 60, 180)
completed_levels: set[int] = set()
_chapter_scroll = 0
_level_scrolls: dict[int, int] = {}
_MENU_TOP = 84
_MENU_BOTTOM = 56
_SCROLL_STEP = 48
_LEVEL_CONCEPT_TOP = 90
_LEVEL_CONCEPT_LINE_H = 17


def _is_back(event):
    return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE


def _scroll_limit(count, cols, card_h, gap, start_y):
    if count <= 0:
        return 0
    rows = (count + cols - 1) // cols
    content_bottom = start_y + rows * card_h + (rows - 1) * gap
    return max(0, content_bottom - (config.HEIGHT - _MENU_BOTTOM))


def is_chapter_unlocked(ch_idx):
    if config.ADMIN_MODE or ch_idx == 0:
        return True
    prev = ch_idx - 1
    offset = chapter_level_offset(prev)
    return all(offset + i in completed_levels for i in range(len(CHAPTERS[prev]["levels"])))


def is_chapter_complete(ch_idx):
    if ch_idx >= len(CHAPTERS):
        return False
    offset = chapter_level_offset(ch_idx)
    return all(offset + i in completed_levels for i in range(len(CHAPTERS[ch_idx]["levels"])))


def chapter_progress(ch_idx):
    if ch_idx >= len(CHAPTERS):
        return 0, 0
    offset = chapter_level_offset(ch_idx)
    total = len(CHAPTERS[ch_idx]["levels"])
    done = sum(1 for i in range(total) if offset + i in completed_levels)
    return done, total


def _wrap_text(font, text, max_width):
    wrapped: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            wrapped.append("")
            continue
        words = paragraph.split(" ")
        current = words[0]
        for word in words[1:]:
            test = f"{current} {word}"
            if font.size(test)[0] <= max_width:
                current = test
            else:
                wrapped.append(current)
                current = word
        wrapped.append(current)
    return wrapped


def _level_list_start_y(chapter_index):
    font = config.game_font(13)
    concept_w = max(180, min(config.WIDTH - 80, 660))
    concept_lines = _wrap_text(font, CHAPTERS[chapter_index].get("concept", ""), concept_w)
    return _LEVEL_CONCEPT_TOP + len(concept_lines) * _LEVEL_CONCEPT_LINE_H + 36


def _draw_menu_buttons(screen, font, labels_colors, start_y, btn_w=260, btn_h=52, gap=16):
    mx, my = pygame.mouse.get_pos()
    buttons = []
    y = start_y
    for label, color in labels_colors:
        rect = pygame.Rect((config.WIDTH - btn_w) // 2, y, btn_w, btn_h)
        hovered = rect.collidepoint(mx, my)
        bg = _PANEL_HOVER if hovered else _PANEL
        border = color if hovered else _PANEL_BORDER

        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        txt = font.render(label, True, color if hovered else WHITE)
        screen.blit(txt, txt.get_rect(center=rect.center))

        buttons.append((rect, label))
        y += btn_h + gap
    return buttons


# ── Main Menu ──

def draw_main_menu(screen):
    screen.fill(_BG_MENU)
    _draw_particles(screen)

    title_font = config.game_font(62, bold=True)
    sub_font = config.game_font(18)

    title = title_font.render("SUPERPOSED", True, _ACCENT)
    screen.blit(title, title.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 120)))

    sub = sub_font.render("A Quantum Computing Puzzle Game", True, LIGHT_GRAY)
    screen.blit(sub, sub.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 70)))

    lw = 260
    pygame.draw.line(screen, _ACCENT_DIM,
                     (config.WIDTH // 2 - lw // 2, config.HEIGHT // 2 - 48),
                     (config.WIDTH // 2 + lw // 2, config.HEIGHT // 2 - 48), 1)

    btn_font = config.game_font(26)
    buttons = _draw_menu_buttons(screen, btn_font, [
        ("Campaign", BLUE),
        ("Sandbox", RED),
        ("Exit", PURPLE),
    ], start_y=config.HEIGHT // 2 - 10)

    from .. import __version__
    ver = config.game_font(12).render(f"v{__version__}", True, DARK_GRAY)
    screen.blit(ver, ver.get_rect(bottomright=(config.WIDTH - 12, config.HEIGHT - 8)))

    return buttons


def handle_main_menu(events, buttons):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if _is_back(event):
            return None, None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, label in buttons:
                if rect.collidepoint(mx, my):
                    if label == "Sandbox":
                        return GameState.SANDBOX, None
                    elif label == "Campaign":
                        return GameState.CHAPTER_SELECT, None
                    elif label == "Exit":
                        return None, None
    return GameState.MAIN_MENU, None


# ── Chapter Select ──

def draw_chapter_select(screen):
    global _chapter_scroll

    screen.fill(_BG_MENU)
    _draw_particles(screen)

    header_font = config.game_font(36, bold=True)
    header = header_font.render("CAMPAIGN", True, WHITE)
    screen.blit(header, header.get_rect(center=(config.WIDTH // 2, 48)))

    card_font = config.game_font(18, bold=True)
    sub_font = config.game_font(13)
    small_font = config.game_font(12)

    cards = []
    cols = 2
    card_w, card_h = 320, 118
    gap = 20
    total_w = cols * card_w + (cols - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    start_y = 100
    _chapter_scroll = min(_chapter_scroll, _scroll_limit(len(CHAPTERS), cols, card_h, gap, start_y))
    clip = pygame.Rect(0, _MENU_TOP, config.WIDTH, max(0, config.HEIGHT - _MENU_TOP - _MENU_BOTTOM))

    mx, my = pygame.mouse.get_pos()

    screen.set_clip(clip)
    for ch_idx, ch in enumerate(CHAPTERS):
        col = ch_idx % cols
        row = ch_idx // cols
        cx = start_x + col * (card_w + gap)
        cy = start_y + row * (card_h + gap) - _chapter_scroll
        rect = pygame.Rect(cx, cy, card_w, card_h)
        visible = rect.clip(clip)
        if visible.width <= 0 or visible.height <= 0:
            continue

        unlocked = is_chapter_unlocked(ch_idx)
        hovered = visible.collidepoint(mx, my) and unlocked

        if not unlocked:
            bg = (18, 18, 22)
            border = (40, 40, 48)
        elif hovered:
            bg = _PANEL_HOVER
            border = ch.get("color", _ACCENT)
        else:
            bg = _PANEL
            border = _PANEL_BORDER

        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        ch_num = small_font.render(f"Chapter {ch_idx + 1}", True, DARK_GRAY)
        screen.blit(ch_num, (cx + 12, cy + 8))

        if is_chapter_complete(ch_idx):
            badge = small_font.render("COMPLETE", True, GREEN)
            screen.blit(badge, badge.get_rect(topright=(cx + card_w - 12, cy + 8)))
        elif not unlocked:
            lock = small_font.render("LOCKED", True, DARK_GRAY)
            screen.blit(lock, lock.get_rect(topright=(cx + card_w - 12, cy + 8)))

        name_color = ch.get("color", LIGHT_GRAY) if (unlocked and hovered) else (WHITE if unlocked else DARK_GRAY)
        name = card_font.render(ch["name"], True, name_color)
        screen.blit(name, (cx + 12, cy + 28))

        sub_color = LIGHT_GRAY if unlocked else DARK_GRAY
        for si, sl in enumerate(_wrap_text(sub_font, ch.get("subtitle", ""), card_w - 24)):
            screen.blit(sub_font.render(sl, True, sub_color), (cx + 12, cy + 52 + si * 16))

        if unlocked:
            done, total = chapter_progress(ch_idx)
            prog = small_font.render(f"{done}/{total}", True, LIGHT_GRAY)
            prog_x = cx + card_w - 12 - prog.get_width()
            bar_w, bar_h = prog_x - cx - 18, 8
            bar_x, bar_y = cx + 12, cy + card_h - 18
            pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if done > 0:
                fill = int(bar_w * done / total)
                c = GREEN if done == total else ch.get("color", CYAN)
                pygame.draw.rect(screen, c, (bar_x, bar_y, fill, bar_h), border_radius=4)
            screen.blit(prog, (prog_x, cy + card_h - 23))

        if unlocked:
            cards.append((visible, ch_idx))
    screen.set_clip(None)

    back_font = config.game_font(18)
    back_txt = back_font.render("← Back (ESC)", True, LIGHT_GRAY)
    back_rect = back_txt.get_rect(topleft=(20, config.HEIGHT - 40))
    screen.blit(back_txt, back_rect)
    cards.append((back_rect, -1))

    return cards


def handle_chapter_select(events, cards):
    global _chapter_scroll

    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if _is_back(event):
            return GameState.MAIN_MENU, None
        if event.type == pygame.MOUSEWHEEL:
            limit = _scroll_limit(len(CHAPTERS), 2, 118, 20, 100)
            _chapter_scroll = max(0, min(limit, _chapter_scroll - event.y * _SCROLL_STEP))
            continue
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, idx in cards:
                if rect.collidepoint(mx, my):
                    if idx == -1:
                        return GameState.MAIN_MENU, None
                    return GameState.LEVEL_SELECT, idx
    return GameState.CHAPTER_SELECT, None


# ── Level Select (per chapter) ──

def draw_level_select(screen, chapter_index):
    ch = CHAPTERS[chapter_index]
    screen.fill(_BG_MENU)
    _draw_particles(screen)

    header_font = config.game_font(28, bold=True)
    sub_font = config.game_font(14)
    card_font = config.game_font(18, bold=True)
    desc_font = config.game_font(13)
    small_font = config.game_font(12)

    ch_color = ch.get("color", CYAN)
    label = sub_font.render(f"Chapter {chapter_index + 1}", True, DARK_GRAY)
    screen.blit(label, label.get_rect(center=(config.WIDTH // 2, 24)))
    header = header_font.render(ch["name"], True, ch_color)
    screen.blit(header, header.get_rect(center=(config.WIDTH // 2, 52)))

    concept_w = max(180, min(config.WIDTH - 80, 660))
    concept_lines = _wrap_text(desc_font, ch.get("concept", ""), concept_w)
    concept_line_h = _LEVEL_CONCEPT_LINE_H
    concept_h = len(concept_lines) * concept_line_h + 20
    concept_top = _LEVEL_CONCEPT_TOP

    offset = chapter_level_offset(chapter_index)
    levels = ch["levels"]

    cards = []
    cols = min(3, len(levels))
    card_w, card_h = 260, 110
    gap = 20
    total_w = cols * card_w + (cols - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    start_y = _level_list_start_y(chapter_index)
    scroll = min(_level_scrolls.get(chapter_index, 0),
                 _scroll_limit(len(levels), cols, card_h, gap, start_y))
    _level_scrolls[chapter_index] = scroll
    clip = pygame.Rect(0, _MENU_TOP, config.WIDTH, max(0, config.HEIGHT - _MENU_TOP - _MENU_BOTTOM))

    mx, my = pygame.mouse.get_pos()

    screen.set_clip(clip)

    cp_x = (config.WIDTH - concept_w - 24) // 2
    cp_y = concept_top - scroll
    cp_rect = pygame.Rect(cp_x, cp_y, concept_w + 24, concept_h)
    pygame.draw.rect(screen, _PANEL, cp_rect, border_radius=10)
    pygame.draw.rect(screen, _PANEL_BORDER, cp_rect, 1, border_radius=10)
    ty = cp_y + 10
    for line in concept_lines:
        if line:
            screen.blit(desc_font.render(line, True, LIGHT_GRAY), (cp_x + 12, ty))
        ty += concept_line_h

    for i, lev in enumerate(levels):
        col = i % cols
        row = i // cols
        cx = start_x + col * (card_w + gap)
        cy = start_y + row * (card_h + gap) - scroll
        rect = pygame.Rect(cx, cy, card_w, card_h)
        visible = rect.clip(clip)
        if visible.width <= 0 or visible.height <= 0:
            continue

        global_idx = offset + i
        done = global_idx in completed_levels
        hovered = visible.collidepoint(mx, my)
        bg = _PANEL_HOVER if hovered else _PANEL
        border = ch_color if hovered else _PANEL_BORDER

        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        num = small_font.render(f"Level {i + 1}", True, DARK_GRAY)
        screen.blit(num, (cx + 10, cy + 8))

        if done:
            badge = small_font.render("DONE", True, GREEN)
            screen.blit(badge, badge.get_rect(topright=(cx + card_w - 10, cy + 8)))

        name = card_font.render(lev["name"], True, ch_color if hovered else WHITE)
        screen.blit(name, (cx + 10, cy + 28))

        desc_lines = _wrap_text(desc_font, lev["description"], card_w - 20)
        dy = cy + 52
        for dl in desc_lines[:2]:
            if dl:
                screen.blit(desc_font.render(dl, True, LIGHT_GRAY), (cx + 10, dy))
            dy += 16

        avail = ", ".join(gid.replace("_", " ").title() for gid in lev["available"])
        avail_txt = small_font.render(f"Tools: {avail}", True, DARK_GRAY)
        screen.blit(avail_txt, (cx + 10, cy + card_h - 22))

        cards.append((visible, global_idx))
    screen.set_clip(None)

    back_font = config.game_font(18)
    back_txt = back_font.render("← Back to chapters (ESC)", True, LIGHT_GRAY)
    back_rect = back_txt.get_rect(topleft=(20, config.HEIGHT - 40))
    screen.blit(back_txt, back_rect)
    cards.append((back_rect, -1))

    return cards


def handle_level_select(events, cards, chapter_index):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if _is_back(event):
            return GameState.CHAPTER_SELECT, None
        if event.type == pygame.MOUSEWHEEL:
            levels = CHAPTERS[chapter_index]["levels"]
            cols = min(3, len(levels))
            limit = _scroll_limit(len(levels), cols, 110, 20, _level_list_start_y(chapter_index))
            scroll = _level_scrolls.get(chapter_index, 0) - event.y * _SCROLL_STEP
            _level_scrolls[chapter_index] = max(0, min(limit, scroll))
            continue
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, idx in cards:
                if rect.collidepoint(mx, my):
                    if idx == -1:
                        return GameState.CHAPTER_SELECT, None
                    return GameState.LEVEL_PLAY, idx
    return GameState.LEVEL_SELECT, None


# ── Win Screen ──

def draw_win_screen(screen, level_index):
    lev = ALL_LEVELS[level_index]

    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    pw, ph = 420, 250
    panel = pygame.Rect((config.WIDTH - pw) // 2, (config.HEIGHT - ph) // 2, pw, ph)
    pygame.draw.rect(screen, _PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, GREEN, panel, 2, border_radius=14)

    tf = config.game_font(32, bold=True)
    title = tf.render("LEVEL COMPLETE!", True, GREEN)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 40)))

    sf = config.game_font(18)
    sub = sf.render(f"{lev['name']} — cleared!", True, LIGHT_GRAY)
    screen.blit(sub, sub.get_rect(center=(panel.centerx, panel.top + 80)))

    ch_idx, _ = _find_chapter(level_index)
    if ch_idx is not None and is_chapter_complete(ch_idx):
        ch = CHAPTERS[ch_idx]
        msg = sf.render(f"Chapter {ch_idx + 1} complete!", True, ch.get("color", GOLD))
        screen.blit(msg, msg.get_rect(center=(panel.centerx, panel.top + 108)))

    btn_font = config.game_font(18, bold=True)
    mx, my = pygame.mouse.get_pos()

    next_rect = pygame.Rect(0, 0, 150, 38)
    next_rect.center = (panel.centerx + 85, panel.bottom - 45)
    next_hov = next_rect.collidepoint(mx, my)
    pygame.draw.rect(screen, CYAN if next_hov else _ACCENT_DIM, next_rect, border_radius=8)
    nt = btn_font.render("NEXT", True, WHITE)
    screen.blit(nt, nt.get_rect(center=next_rect.center))

    menu_rect = pygame.Rect(0, 0, 150, 38)
    menu_rect.center = (panel.centerx - 85, panel.bottom - 45)
    menu_hov = menu_rect.collidepoint(mx, my)
    pygame.draw.rect(screen, DARK_GRAY if not menu_hov else LIGHT_GRAY, menu_rect, border_radius=8)
    mt = btn_font.render("CHAPTERS", True, WHITE)
    screen.blit(mt, mt.get_rect(center=menu_rect.center))

    return menu_rect, next_rect


def _find_chapter(level_index):
    offset = 0
    for ch_idx, ch in enumerate(CHAPTERS):
        n = len(ch["levels"])
        if offset <= level_index < offset + n:
            return ch_idx, level_index - offset
        offset += n
    return None, None


def _next_level_index(level_index):
    ch_idx, local_idx = _find_chapter(level_index)
    if ch_idx is None:
        return None
    ch = CHAPTERS[ch_idx]
    if local_idx + 1 < len(ch["levels"]):
        return level_index + 1
    if ch_idx + 1 < len(CHAPTERS) and is_chapter_unlocked(ch_idx + 1):
        return chapter_level_offset(ch_idx + 1)
    return None


def handle_win_screen(events, menu_btn, next_btn, level_index):
    mx, my = pygame.mouse.get_pos()
    nxt = _next_level_index(level_index)
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameState.CHAPTER_SELECT, None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and nxt is not None:
                return GameState.LEVEL_PLAY, nxt
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if menu_btn.collidepoint(mx, my):
                return GameState.CHAPTER_SELECT, None
            if next_btn.collidepoint(mx, my):
                if nxt is not None:
                    return GameState.LEVEL_PLAY, nxt
                return GameState.CHAPTER_SELECT, None
    return GameState.WIN_SCREEN, level_index
