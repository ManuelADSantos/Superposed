"""Superposed: A Quantum Factory Puzzle Game.

Entry point — state-machine game loop with menu, levels, and sandbox.
"""

import pygame

import config
from config import FPS, BG
from entities import BuildingType, Direction
from input_handler import handle_input
from simulation import update_items
from rendering import draw_grid, draw_ui
from menu import (
    GameState,
    draw_main_menu, handle_main_menu,
    draw_level_select, handle_level_select,
    draw_briefing, handle_briefing,
    draw_win_screen, handle_win_screen,
    completed_levels,
)
from levels import ALL_LEVELS
from world import reset_world, load_level, check_win_condition
import world as W


def main():
    pygame.init()

    # Maximised window (not fullscreen)
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    # Fallback if Info() returns nonsense before a display exists
    if sw < 640 or sh < 480:
        sw, sh = 1440, 900
    config.WIDTH = sw - 20
    config.HEIGHT = sh - 100  # room for macOS menu bar + dock

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Superposed — Quantum Factory")
    clock = pygame.time.Clock()

    # ── State machine ────────────────────────────────────────────────────
    state = GameState.MAIN_MENU
    level_index = 0

    # Gameplay state (persists across state transitions within a session)
    selected_building = BuildingType.BELT
    selected_rotation = Direction.RIGHT
    paused = False
    step_requested = False

    # UI elements returned by draw functions for click detection
    ui_elements = None

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()

        # Check for quit / resize in any state
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                config.WIDTH, config.HEIGHT = ev.w, ev.h
                screen = pygame.display.set_mode(
                    (config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

        if not running:
            break

        # ── MAIN MENU ────────────────────────────────────────────────────
        if state == GameState.MAIN_MENU:
            buttons = draw_main_menu(screen)
            new_state, _ = handle_main_menu(events, buttons)
            if new_state is None:
                running = False
            elif new_state == GameState.SANDBOX:
                reset_world()
                selected_building = BuildingType.BELT
                paused = False
                state = GameState.SANDBOX
            elif new_state != state:
                state = new_state

        # ── LEVEL SELECT ─────────────────────────────────────────────────
        elif state == GameState.LEVEL_SELECT:
            cards = draw_level_select(screen)
            new_state, idx = handle_level_select(events, cards)
            if new_state is None:
                running = False
            elif new_state == GameState.BRIEFING:
                level_index = idx
                state = GameState.BRIEFING
            elif new_state != state:
                state = new_state

        # ── BRIEFING (pre-level overlay) ─────────────────────────────────
        elif state == GameState.BRIEFING:
            # Draw the level in the background (or black)
            screen.fill(BG)
            start_btn = draw_briefing(screen, level_index)
            new_state, idx = handle_briefing(events, start_btn, level_index)
            if new_state is None:
                running = False
            elif new_state == GameState.LEVEL_PLAY:
                load_level(ALL_LEVELS[level_index], level_index)
                selected_building = BuildingType.BELT
                paused = False
                # Ensure selected building is valid for this level
                avail = W.available_buildings
                if avail and selected_building not in avail:
                    selected_building = avail[0]
                state = GameState.LEVEL_PLAY
            elif new_state != state:
                if idx is not None:
                    level_index = idx
                state = new_state

        # ── WIN SCREEN ───────────────────────────────────────────────────
        elif state == GameState.WIN_SCREEN:
            # Keep drawing the game underneath
            screen.fill(BG)
            draw_grid(screen)
            draw_ui(screen, selected_building, selected_rotation, paused)
            menu_btn, next_btn = draw_win_screen(screen, level_index)
            new_state, idx = handle_win_screen(events, menu_btn, next_btn, level_index)
            if new_state is None:
                running = False
            elif new_state == GameState.BRIEFING:
                level_index = idx
                state = GameState.BRIEFING
            elif new_state == GameState.LEVEL_SELECT:
                state = GameState.LEVEL_SELECT
            elif new_state != state:
                state = new_state

        # ── SANDBOX / LEVEL PLAY ─────────────────────────────────────────
        elif state in (GameState.SANDBOX, GameState.LEVEL_PLAY):
            # Re-inject events into pygame queue so handle_input can get them
            for ev in events:
                pygame.event.post(ev)

            result = handle_input(
                dt, selected_building, selected_rotation, paused, step_requested
            )
            run_ok, selected_building, selected_rotation, paused, step_requested, back_to_menu = result

            if not run_ok:
                if state == GameState.LEVEL_PLAY:
                    state = GameState.LEVEL_SELECT
                    continue
                else:
                    running = False
                    continue

            if back_to_menu:
                if state == GameState.LEVEL_PLAY:
                    state = GameState.LEVEL_SELECT
                else:
                    state = GameState.MAIN_MENU
                continue

            if not paused or step_requested:
                update_items(dt)
                step_requested = False

            # Check win condition for levels
            if state == GameState.LEVEL_PLAY and check_win_condition():
                completed_levels.add(level_index)
                state = GameState.WIN_SCREEN

            screen.fill(BG)
            draw_grid(screen)
            draw_ui(screen, selected_building, selected_rotation, paused)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
