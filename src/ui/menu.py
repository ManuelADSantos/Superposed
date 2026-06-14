"""Menu screens: main menu, level select, briefing overlay, and win screen."""

from __future__ import annotations

import pygame
from enum import Enum

from ..core import config
from ..core.config import (
    BG, WHITE, LIGHT_GRAY, DARK_GRAY, YELLOW, GREEN,
    RED, BLUE, PURPLE, CYAN, GOLD, TEAL,
)
from ..content.levels import ALL_LEVELS


class GameState(Enum):
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    SANDBOX = 2
    LEVEL_PLAY = 3
    BRIEFING = 4
    WIN_SCREEN = 5


_BG_MENU = (10, 10, 14)
_PANEL = (24, 24, 30)
_PANEL_HOVER = (34, 34, 44)
_PANEL_BORDER = (55, 55, 70)
_ACCENT = PURPLE
_ACCENT_DIM = (120, 60, 180)

completed_levels: set[int] = set()


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


def draw_main_menu(screen):
    screen.fill(_BG_MENU)

    title_font = pygame.font.SysFont("consolas", 52, bold=True)
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
        ("Levels", CYAN),
        ("Sandbox", GREEN),
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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return None, None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, label in buttons:
                if rect.collidepoint(mx, my):
                    if label == "Sandbox":
                        return GameState.SANDBOX, None
                    elif label == "Levels":
                        return GameState.LEVEL_SELECT, None
    return GameState.MAIN_MENU, None


def draw_level_select(screen):
    screen.fill(_BG_MENU)

    header_font = pygame.font.SysFont("consolas", 36, bold=True)
    header = header_font.render("SELECT LEVEL", True, WHITE)
    screen.blit(header, header.get_rect(center=(config.WIDTH // 2, 48)))

    card_font = pygame.font.SysFont("consolas", 18, bold=True)
    desc_font = pygame.font.SysFont("consolas", 13)
    small_font = pygame.font.SysFont("consolas", 12)

    cards = []
    cols = 4
    card_w, card_h = 250, 120
    gap = 20
    total_w = cols * card_w + (cols - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    start_y = 100

    mx, my = pygame.mouse.get_pos()

    for i, lev in enumerate(ALL_LEVELS):
        col = i % cols
        row = i // cols
        cx = start_x + col * (card_w + gap)
        cy = start_y + row * (card_h + gap)
        rect = pygame.Rect(cx, cy, card_w, card_h)

        hovered = rect.collidepoint(mx, my)
        bg = _PANEL_HOVER if hovered else _PANEL
        border = _ACCENT if hovered else _PANEL_BORDER

        pygame.draw.rect(screen, bg, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)

        num = small_font.render(f"Level {i + 1}", True, DARK_GRAY)
        screen.blit(num, (cx + 10, cy + 8))

        if i in completed_levels:
            badge = small_font.render("DONE", True, GREEN)
            screen.blit(badge, badge.get_rect(topright=(cx + card_w - 10, cy + 8)))

        name = card_font.render(lev["name"], True, CYAN if hovered else WHITE)
        screen.blit(name, (cx + 10, cy + 28))

        desc_lines = _wrap_text(desc_font, lev["description"], card_w - 20)
        clip = pygame.Rect(cx + 10, cy + 54, card_w - 20, card_h - 80)
        screen.set_clip(clip)
        dy = cy + 54
        for dl in desc_lines:
            if dl:
                screen.blit(desc_font.render(dl, True, LIGHT_GRAY), (cx + 10, dy))
            dy += 16
        screen.set_clip(None)

        avail = ", ".join(gid.replace("_", " ").title() for gid in lev["available"])
        avail_txt = small_font.render(f"Tools: {avail}", True, DARK_GRAY)
        screen.blit(avail_txt, (cx + 10, cy + card_h - 22))

        cards.append((rect, i))

    back_font = pygame.font.SysFont("consolas", 18)
    back_txt = back_font.render("← Back", True, LIGHT_GRAY)
    back_rect = back_txt.get_rect(topleft=(20, config.HEIGHT - 40))
    screen.blit(back_txt, back_rect)
    cards.append((back_rect, -1))

    return cards


def handle_level_select(events, cards):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return GameState.MAIN_MENU, None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, idx in cards:
                if rect.collidepoint(mx, my):
                    if idx == -1:
                        return GameState.MAIN_MENU, None
                    return GameState.BRIEFING, idx
    return GameState.LEVEL_SELECT, None


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

    title = tf.render(f"Level {level_index + 1}: {lev['name']}", True, CYAN)
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
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return GameState.LEVEL_PLAY, level_index
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_btn.collidepoint(mx, my):
                return GameState.LEVEL_PLAY, level_index
    return GameState.BRIEFING, level_index


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

    btn_font = pygame.font.SysFont("consolas", 18, bold=True)
    mx, my = pygame.mouse.get_pos()

    next_rect = pygame.Rect(0, 0, 150, 38)
    next_rect.center = (panel.centerx + 85, panel.bottom - 45)
    next_hov = next_rect.collidepoint(mx, my)
    pygame.draw.rect(screen, CYAN if next_hov else _ACCENT_DIM, next_rect, border_radius=8)
    nt = btn_font.render("NEXT LEVEL", True, WHITE)
    screen.blit(nt, nt.get_rect(center=next_rect.center))

    menu_rect = pygame.Rect(0, 0, 150, 38)
    menu_rect.center = (panel.centerx - 85, panel.bottom - 45)
    menu_hov = menu_rect.collidepoint(mx, my)
    pygame.draw.rect(screen, DARK_GRAY if not menu_hov else LIGHT_GRAY, menu_rect, border_radius=8)
    mt = btn_font.render("MENU", True, WHITE if menu_hov else LIGHT_GRAY)
    screen.blit(mt, mt.get_rect(center=menu_rect.center))

    return menu_rect, next_rect


def handle_win_screen(events, menu_btn, next_btn, level_index):
    mx, my = pygame.mouse.get_pos()
    for event in events:
        if event.type == pygame.QUIT:
            return None, None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return GameState.LEVEL_SELECT, None
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                nxt = level_index + 1
                if nxt < len(ALL_LEVELS):
                    return GameState.BRIEFING, nxt
                return GameState.LEVEL_SELECT, None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if menu_btn.collidepoint(mx, my):
                return GameState.LEVEL_SELECT, None
            if next_btn.collidepoint(mx, my):
                nxt = level_index + 1
                if nxt < len(ALL_LEVELS):
                    return GameState.BRIEFING, nxt
                return GameState.LEVEL_SELECT, None
    return GameState.WIN_SCREEN, level_index
