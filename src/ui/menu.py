"""Menu screens: main menu, chapter select, level select, briefing, concept intro, and win screen."""

from __future__ import annotations

import random
import pygame
from enum import Enum

from ..core import config
from ..core.config import (
    BG, WHITE, LIGHT_GRAY, DARK_GRAY, YELLOW, GREEN,
    RED, BLUE, PURPLE, CYAN, GOLD, TEAL,
)
from ..content.levels import CHAPTERS, COMING_SOON, ALL_LEVELS, chapter_level_offset


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
    BRIEFING = 5
    WIN_SCREEN = 6
    CONCEPT_INTRO = 7


_BG_MENU = (10, 10, 14)
_PANEL = (24, 24, 30)
_PANEL_HOVER = (34, 34, 44)
_PANEL_BORDER = (55, 55, 70)
_ACCENT = PURPLE
_ACCENT_DIM = (120, 60, 180)
completed_levels: set[int] = set()


def _is_back(event):
    return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE


def is_chapter_unlocked(ch_idx):
    if config.ADMIN_MODE or ch_idx == 0:
        return True
    prev = ch_idx - 1
    if prev >= len(CHAPTERS):
        return False
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

    title_font = pygame.font.SysFont("consolas", 62, bold=True)
    sub_font = pygame.font.SysFont("consolas", 18)

    title = title_font.render("SUPERPOSED", True, _ACCENT)
    screen.blit(title, title.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 120)))

    sub = sub_font.render("A Quantum Computing Puzzle Game", True, LIGHT_GRAY)
    screen.blit(sub, sub.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 70)))

    lw = 260
    pygame.draw.line(screen, _ACCENT_DIM,
                     (config.WIDTH // 2 - lw // 2, config.HEIGHT // 2 - 48),
                     (config.WIDTH // 2 + lw // 2, config.HEIGHT // 2 - 48), 1)

    btn_font = pygame.font.SysFont("consolas", 26)
    buttons = _draw_menu_buttons(screen, btn_font, [
        ("Campaign", CYAN),
        ("Sandbox", GREEN),
        ("Exit", DARK_GRAY),
    ], start_y=config.HEIGHT // 2 - 10)

    from .. import __version__
    ver = pygame.font.SysFont("consolas", 12).render(f"v{__version__}", True, DARK_GRAY)
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
    screen.fill(_BG_MENU)
    _draw_particles(screen)

    header_font = pygame.font.SysFont("consolas", 36, bold=True)
    header = header_font.render("CAMPAIGN", True, WHITE)
    screen.blit(header, header.get_rect(center=(config.WIDTH // 2, 48)))

    card_font = pygame.font.SysFont("consolas", 18, bold=True)
    sub_font = pygame.font.SysFont("consolas", 13)
    small_font = pygame.font.SysFont("consolas", 12)

    cards = []
    cols = 2
    card_w, card_h = 320, 118
    gap = 20
    total_w = cols * card_w + (cols - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    start_y = 100

    mx, my = pygame.mouse.get_pos()

    all_chapters = [(i, ch, True) for i, ch in enumerate(CHAPTERS)]
    all_chapters += [(len(CHAPTERS) + i, {"name": cs["name"], "subtitle": cs["subtitle"]}, False)
                     for i, cs in enumerate(COMING_SOON)]

    for display_idx, (ch_idx, ch, playable) in enumerate(all_chapters):
        col = display_idx % cols
        row = display_idx // cols
        cx = start_x + col * (card_w + gap)
        cy = start_y + row * (card_h + gap)
        rect = pygame.Rect(cx, cy, card_w, card_h)

        unlocked = playable and is_chapter_unlocked(ch_idx)
        hovered = rect.collidepoint(mx, my) and unlocked

        if not unlocked:
            bg = (18, 18, 22)
            border = (40, 40, 48)
        elif hovered:
            bg = _PANEL_HOVER
            border = ch.get("color", _ACCENT) if playable else _PANEL_BORDER
        else:
            bg = _PANEL
            border = _PANEL_BORDER

        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        ch_num = small_font.render(f"Chapter {ch_idx + 1}", True, DARK_GRAY)
        screen.blit(ch_num, (cx + 12, cy + 8))

        if playable and is_chapter_complete(ch_idx):
            badge = small_font.render("COMPLETE", True, GREEN)
            screen.blit(badge, badge.get_rect(topright=(cx + card_w - 12, cy + 8)))
        elif not playable:
            lock = small_font.render("COMING SOON", True, DARK_GRAY)
            screen.blit(lock, lock.get_rect(topright=(cx + card_w - 12, cy + 8)))
        elif not unlocked:
            lock = small_font.render("LOCKED", True, DARK_GRAY)
            screen.blit(lock, lock.get_rect(topright=(cx + card_w - 12, cy + 8)))

        name_color = ch.get("color", LIGHT_GRAY) if (unlocked and hovered) else (WHITE if unlocked else DARK_GRAY)
        name = card_font.render(ch["name"], True, name_color)
        screen.blit(name, (cx + 12, cy + 28))

        sub_color = LIGHT_GRAY if unlocked else DARK_GRAY
        for si, sl in enumerate(_wrap_text(sub_font, ch.get("subtitle", ""), card_w - 24)):
            screen.blit(sub_font.render(sl, True, sub_color), (cx + 12, cy + 52 + si * 16))

        if playable and unlocked:
            done, total = chapter_progress(ch_idx)
            bar_w, bar_h = card_w - 24, 8
            bar_x, bar_y = cx + 12, cy + card_h - 18
            pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if done > 0:
                fill = int(bar_w * done / total)
                c = GREEN if done == total else ch.get("color", CYAN)
                pygame.draw.rect(screen, c, (bar_x, bar_y, fill, bar_h), border_radius=4)
            prog = small_font.render(f"{done}/{total}", True, LIGHT_GRAY)
            screen.blit(prog, prog.get_rect(topright=(cx + card_w - 12, cy + card_h - 20)))

        if unlocked:
            cards.append((rect, ch_idx))

    back_font = pygame.font.SysFont("consolas", 18)
    back_txt = back_font.render("<< Back", True, LIGHT_GRAY)
    back_rect = back_txt.get_rect(topleft=(20, config.HEIGHT - 40))
    screen.blit(back_txt, back_rect)
    cards.append((back_rect, -1))

    return cards


def handle_chapter_select(events, cards):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if _is_back(event):
            return GameState.MAIN_MENU, None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, idx in cards:
                if rect.collidepoint(mx, my):
                    if idx == -1:
                        return GameState.MAIN_MENU, None
                    return GameState.CONCEPT_INTRO, idx
    return GameState.CHAPTER_SELECT, None


# ── Concept Intro (chapter overview) ──

def draw_concept_intro(screen, chapter_index):
    ch = CHAPTERS[chapter_index]
    screen.fill(_BG_MENU)
    _draw_particles(screen)

    tf = pygame.font.SysFont("consolas", 30, bold=True)
    sf = pygame.font.SysFont("consolas", 14)
    bf = pygame.font.SysFont("consolas", 22, bold=True)

    pw = 580
    pad = 28
    text_w = pw - pad * 2
    line_h = 19

    lines = _wrap_text(sf, ch["concept"], text_w)
    text_h = len(lines) * line_h
    title_h = 64
    btn_h = 58
    ph = min(title_h + text_h + btn_h, config.HEIGHT - 20)

    panel = pygame.Rect((config.WIDTH - pw) // 2, max(10, (config.HEIGHT - ph) // 2), pw, ph)
    pygame.draw.rect(screen, _PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, ch.get("color", _ACCENT), panel, 2, border_radius=14)

    ch_label = sf.render(f"Chapter {chapter_index + 1}", True, DARK_GRAY)
    screen.blit(ch_label, ch_label.get_rect(midtop=(panel.centerx, panel.top + 10)))

    title = tf.render(ch["name"], True, ch.get("color", CYAN))
    screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.top + 28)))

    clip = pygame.Rect(panel.left + pad, panel.top + title_h,
                       text_w, ph - title_h - btn_h)
    screen.set_clip(clip)
    y = panel.top + title_h
    for line in lines:
        if line:
            txt = sf.render(line, True, LIGHT_GRAY)
            screen.blit(txt, (panel.left + pad, y))
        y += line_h
    screen.set_clip(None)

    btn_rect = pygame.Rect(0, 0, 200, 40)
    btn_rect.center = (panel.centerx, panel.bottom - 30)

    mx, my = pygame.mouse.get_pos()
    hovered = btn_rect.collidepoint(mx, my)
    c = ch.get("color", _ACCENT)
    pygame.draw.rect(screen, c if hovered else _ACCENT_DIM, btn_rect, border_radius=8)
    btn_text = bf.render("VIEW LEVELS", True, WHITE)
    screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    return btn_rect


def handle_concept_intro(events, btn_rect, chapter_index):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameState.CHAPTER_SELECT, None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return GameState.LEVEL_SELECT, chapter_index
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_rect.collidepoint(mx, my):
                return GameState.LEVEL_SELECT, chapter_index
    return GameState.CONCEPT_INTRO, chapter_index


# ── Level Select (per chapter) ──

def draw_level_select(screen, chapter_index):
    ch = CHAPTERS[chapter_index]
    screen.fill(_BG_MENU)
    _draw_particles(screen)

    header_font = pygame.font.SysFont("consolas", 28, bold=True)
    sub_font = pygame.font.SysFont("consolas", 14)
    card_font = pygame.font.SysFont("consolas", 18, bold=True)
    desc_font = pygame.font.SysFont("consolas", 13)
    small_font = pygame.font.SysFont("consolas", 12)

    ch_color = ch.get("color", CYAN)
    label = sub_font.render(f"Chapter {chapter_index + 1}", True, DARK_GRAY)
    screen.blit(label, label.get_rect(center=(config.WIDTH // 2, 24)))
    header = header_font.render(ch["name"], True, ch_color)
    screen.blit(header, header.get_rect(center=(config.WIDTH // 2, 52)))

    offset = chapter_level_offset(chapter_index)
    levels = ch["levels"]

    cards = []
    cols = min(3, len(levels))
    card_w, card_h = 260, 110
    gap = 20
    total_w = cols * card_w + (cols - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    start_y = 100

    mx, my = pygame.mouse.get_pos()

    for i, lev in enumerate(levels):
        col = i % cols
        row = i // cols
        cx = start_x + col * (card_w + gap)
        cy = start_y + row * (card_h + gap)
        rect = pygame.Rect(cx, cy, card_w, card_h)

        global_idx = offset + i
        done = global_idx in completed_levels
        hovered = rect.collidepoint(mx, my)
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

        cards.append((rect, global_idx))

    back_font = pygame.font.SysFont("consolas", 18)
    back_txt = back_font.render("<< Back to chapters", True, LIGHT_GRAY)
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, idx in cards:
                if rect.collidepoint(mx, my):
                    if idx == -1:
                        return GameState.CHAPTER_SELECT, None
                    return GameState.BRIEFING, idx
    return GameState.LEVEL_SELECT, None


# ── Briefing ──

def draw_briefing(screen, level_index):
    lev = ALL_LEVELS[level_index]

    tf = pygame.font.SysFont("consolas", 28, bold=True)
    bf = pygame.font.SysFont("consolas", 15)
    btn_font = pygame.font.SysFont("consolas", 22, bold=True)

    pw = 520
    pad_x = 24
    text_area_w = pw - pad_x * 2
    line_h = 22
    title_h = 60
    btn_h = 70

    lines = _wrap_text(bf, lev["briefing"], text_area_w)
    text_block_h = len(lines) * line_h

    ph = min(title_h + text_block_h + btn_h, config.HEIGHT - 40)

    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect((config.WIDTH - pw) // 2, (config.HEIGHT - ph) // 2, pw, ph)
    pygame.draw.rect(screen, _PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, _ACCENT, panel, 2, border_radius=14)

    title = tf.render(lev["name"], True, CYAN)
    screen.blit(title, title.get_rect(midtop=(panel.centerx, panel.top + 18)))

    clip = pygame.Rect(panel.left + pad_x, panel.top + title_h,
                       text_area_w, ph - title_h - btn_h)
    screen.set_clip(clip)
    y = panel.top + title_h
    for line in lines:
        if line:
            txt = bf.render(line, True, LIGHT_GRAY)
            screen.blit(txt, (panel.left + pad_x, y))
        y += line_h
    screen.set_clip(None)

    btn_rect = pygame.Rect(0, 0, 180, 44)
    btn_rect.center = (panel.centerx, panel.bottom - 40)

    mx, my = pygame.mouse.get_pos()
    hovered = btn_rect.collidepoint(mx, my)
    pygame.draw.rect(screen, _ACCENT if hovered else _ACCENT_DIM, btn_rect, border_radius=8)
    start = btn_font.render("START", True, WHITE)
    screen.blit(start, start.get_rect(center=btn_rect.center))

    return btn_rect


def handle_briefing(events, start_btn, level_index):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameState.LEVEL_SELECT, None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return GameState.LEVEL_PLAY, level_index
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_btn.collidepoint(mx, my):
                return GameState.LEVEL_PLAY, level_index
    return GameState.BRIEFING, level_index


# ── Win Screen ──

def draw_win_screen(screen, level_index):
    lev = ALL_LEVELS[level_index]

    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    pw, ph = 400, 220
    panel = pygame.Rect((config.WIDTH - pw) // 2, (config.HEIGHT - ph) // 2, pw, ph)
    pygame.draw.rect(screen, _PANEL, panel, border_radius=14)
    pygame.draw.rect(screen, GREEN, panel, 2, border_radius=14)

    tf = pygame.font.SysFont("consolas", 32, bold=True)
    title = tf.render("LEVEL COMPLETE!", True, GREEN)
    screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 40)))

    sf = pygame.font.SysFont("consolas", 18)
    sub = sf.render(f"{lev['name']} — cleared!", True, LIGHT_GRAY)
    screen.blit(sub, sub.get_rect(center=(panel.centerx, panel.top + 80)))

    ch_idx, _ = _find_chapter(level_index)
    if ch_idx is not None and is_chapter_complete(ch_idx):
        ch = CHAPTERS[ch_idx]
        msg = sf.render(f"Chapter {ch_idx + 1} complete!", True, ch.get("color", GOLD))
        screen.blit(msg, msg.get_rect(center=(panel.centerx, panel.top + 108)))

    btn_font = pygame.font.SysFont("consolas", 18, bold=True)
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
    mt = btn_font.render("CHAPTERS", True, WHITE if menu_hov else LIGHT_GRAY)
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
                return GameState.BRIEFING, nxt
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if menu_btn.collidepoint(mx, my):
                return GameState.CHAPTER_SELECT, None
            if next_btn.collidepoint(mx, my):
                if nxt is not None:
                    return GameState.BRIEFING, nxt
                return GameState.CHAPTER_SELECT, None
    return GameState.WIN_SCREEN, level_index
