"""Superposed: A Quantum Factory Puzzle Game."""

from __future__ import annotations

import pygame
from .core import config, audio
from .core.config import FPS, BG

from .engine.gate_registry import load_gates, BELT

from .core.entities import Direction
from .ui.input_handler import handle_input
from .engine.simulation import update_items
from .ui.rendering import draw_grid, draw_ui, tick_toast, reset_briefing, draw_briefing_overlay
from .ui.menu import (
    GameState,
    draw_main_menu, handle_main_menu,
    draw_chapter_select, handle_chapter_select,
    draw_level_select, handle_level_select,
    draw_win_screen, handle_win_screen,
    completed_levels, _find_chapter,
)
from .content.levels import ALL_LEVELS
from .core.world import reset_world, load_level, check_win_condition
from .core import world as W


def main():
    audio.pre_init()
    pygame.init()

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    if sw < 640 or sh < 480:
        sw, sh = 1440, 900
    config.WIDTH = sw - 20
    config.HEIGHT = sh - 100

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Superposed — Quantum Factory")
    clock = pygame.time.Clock()

    load_gates()
    audio.init()
    audio.play_music()
    audio.toggle_mute()
    print(f"[Superposed] font: {config.FONT_PATH}")

    state = GameState.MAIN_MENU
    level_index = 0
    chapter_index = 0
    selected_building = BELT
    selected_rotation = Direction.RIGHT
    paused = False
    show_briefing = False
    running = True

    def _load_and_start(idx):
        nonlocal level_index, selected_building, paused, show_briefing
        level_index = idx
        load_level(ALL_LEVELS[level_index], level_index)
        reset_briefing()
        selected_building = BELT
        paused = False
        avail = W.available_buildings
        if avail and selected_building not in avail:
            selected_building = avail[0]
        show_briefing = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_m:
                audio.toggle_mute()
            elif ev.type == pygame.VIDEORESIZE:
                config.WIDTH, config.HEIGHT = ev.w, ev.h
                screen = pygame.display.set_mode(
                    (config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

        if not running:
            break

        tick_toast(dt)

        if state == GameState.MAIN_MENU:
            buttons = draw_main_menu(screen)
            new_state, _ = handle_main_menu(events, buttons)
            if new_state is None:
                running = False
            elif new_state == GameState.SANDBOX:
                reset_world()
                selected_building = BELT
                paused = False
                state = GameState.SANDBOX
            elif new_state != state:
                state = new_state

        elif state == GameState.CHAPTER_SELECT:
            cards = draw_chapter_select(screen)
            new_state, idx = handle_chapter_select(events, cards)
            if new_state is None:
                running = False
            elif new_state == GameState.LEVEL_SELECT:
                chapter_index = idx
                state = GameState.LEVEL_SELECT
            elif new_state != state:
                state = new_state

        elif state == GameState.LEVEL_SELECT:
            cards = draw_level_select(screen, chapter_index)
            new_state, idx = handle_level_select(events, cards, chapter_index)
            if new_state is None:
                running = False
            elif new_state == GameState.LEVEL_PLAY:
                _load_and_start(idx)
                state = GameState.LEVEL_PLAY
            elif new_state != state:
                state = new_state

        elif state == GameState.WIN_SCREEN:
            screen.fill(BG)
            draw_grid(screen)
            draw_ui(screen, selected_building, selected_rotation, paused)
            menu_btn, next_btn = draw_win_screen(screen, level_index)
            new_state, idx = handle_win_screen(events, menu_btn, next_btn, level_index)
            if new_state is None:
                running = False
            elif new_state == GameState.LEVEL_PLAY:
                ch_idx, _ = _find_chapter(idx)
                if ch_idx is not None:
                    chapter_index = ch_idx
                _load_and_start(idx)
                state = GameState.LEVEL_PLAY
            elif new_state == GameState.CHAPTER_SELECT:
                state = GameState.CHAPTER_SELECT
            elif new_state != state:
                state = new_state

        elif state in (GameState.SANDBOX, GameState.LEVEL_PLAY):
            if show_briefing and state == GameState.LEVEL_PLAY:
                screen.fill(BG)
                draw_grid(screen)
                draw_ui(screen, selected_building, selected_rotation, paused)
                draw_briefing_overlay(screen, "Click anywhere to begin", force=True)
                for ev in events:
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        show_briefing = False
                        state = GameState.LEVEL_SELECT
                    elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                        show_briefing = False
            else:
                result = handle_input(
                    dt, selected_building, selected_rotation, paused,
                    events=events,
                )
                run_ok, selected_building, selected_rotation, paused, back_to_menu = result

                if not run_ok:
                    state = GameState.CHAPTER_SELECT if state == GameState.LEVEL_PLAY else GameState.MAIN_MENU
                    if state == GameState.MAIN_MENU:
                        running = False
                    continue

                if back_to_menu:
                    state = GameState.CHAPTER_SELECT if state == GameState.LEVEL_PLAY else GameState.MAIN_MENU
                    continue

                if not paused:
                    update_items(dt * config.SPEED_MULT)

                if state == GameState.LEVEL_PLAY and check_win_condition():
                    completed_levels.add(level_index)
                    audio.play_sfx('win')
                    state = GameState.WIN_SCREEN

                screen.fill(BG)
                draw_grid(screen)
                draw_ui(screen, selected_building, selected_rotation, paused)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
