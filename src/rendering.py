"""Rendering and UI drawing."""

import pygame
import world as world_module

from config import (
    WIDTH, HEIGHT, TILE_SIZE, BG, GRID, WHITE, YELLOW, RED, GREEN, BLUE, PURPLE
)
from entities import BuildingType, QubitState, DIR_VECTORS, state_color
from world import world, get_tile, world_to_screen, screen_to_world


def draw_arrow(surface, rect, direction, color=WHITE):
    """Draw a directional arrow in the center of a rect."""
    cx = rect.centerx
    cy = rect.centery

    if direction.value == 0:  # UP
        points = [(cx, cy - 12), (cx - 10, cy + 8), (cx + 10, cy + 8)]
    elif direction.value == 1:  # RIGHT
        points = [(cx + 12, cy), (cx - 8, cy - 10), (cx - 8, cy + 10)]
    elif direction.value == 2:  # DOWN
        points = [(cx, cy + 12), (cx - 10, cy - 8), (cx + 10, cy - 8)]
    else:  # LEFT
        points = [(cx - 12, cy), (cx + 8, cy - 10), (cx + 8, cy + 10)]

    pygame.draw.polygon(surface, color, points)


def draw_building_label(surface, rect, label, color=WHITE):
    """Draw a text label in the center of a rect."""
    font = pygame.font.SysFont("consolas", 18)
    text = font.render(label, True, color)
    text_rect = text.get_rect(center=rect.center)
    surface.blit(text, text_rect)


def draw_measurement_histogram(surface, rect, tile):
    """Draw a measurement histogram and flash on a measurement gate."""
    if tile.measurements:
        chart_rect = rect.inflate(-14, -22)
        chart_rect.height = max(16, chart_rect.height // 2)
        chart_rect.top = rect.top + 6

        zero_count = sum(1 for outcome in tile.measurements if outcome == QubitState.ZERO)
        one_count = sum(1 for outcome in tile.measurements if outcome == QubitState.ONE)
        total = max(1, zero_count + one_count)

        gap = 4
        bar_width = max(4, (chart_rect.width - gap) // 2)
        max_height = chart_rect.height - 4

        red_height = max(4, int(max_height * (zero_count / total)))
        blue_height = max(4, int(max_height * (one_count / total)))

        red_rect = pygame.Rect(chart_rect.left, chart_rect.bottom - red_height, bar_width, red_height)
        blue_rect = pygame.Rect(chart_rect.left + bar_width + gap, chart_rect.bottom - blue_height, bar_width, blue_height)

        pygame.draw.rect(surface, RED, red_rect)
        pygame.draw.rect(surface, BLUE, blue_rect)
        pygame.draw.rect(surface, WHITE, chart_rect, 1)

        timeline_y = chart_rect.bottom + 2
        timeline_width = chart_rect.width
        tick_width = max(2, timeline_width // 12)
        start_x = chart_rect.left

        for index, outcome in enumerate(tile.measurements[-12:]):
            tick_rect = pygame.Rect(start_x + index * tick_width, timeline_y, tick_width - 1, 4)
            pygame.draw.rect(surface, state_color(outcome), tick_rect)

    if tile.measure_flash > 0:
        alpha = int(180 * min(tile.measure_flash / 0.35, 1.0))
        flash_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(flash_surface, (255, 255, 255, alpha), flash_surface.get_rect(), 4, border_radius=6)
        surface.blit(flash_surface, rect.topleft)


def draw_grid(surface):
    """Draw the world grid and all buildings."""
    size = TILE_SIZE * world_module.zoom

    start_x = int(world_module.camera_x // size)
    end_x = int((world_module.camera_x + WIDTH) // size) + 2

    start_y = int(world_module.camera_y // size)
    end_y = int((world_module.camera_y + HEIGHT) // size) + 2

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            sx, sy = world_to_screen(x, y, TILE_SIZE)
            rect = pygame.Rect(sx, sy, size, size)

            pygame.draw.rect(surface, GRID, rect, 1)

            tile = get_tile(x, y)

            # Draw building
            if tile.building == BuildingType.BELT:
                pygame.draw.rect(surface, BLUE, rect.inflate(-10, -10), border_radius=6)
                draw_arrow(surface, rect, tile.direction)

            elif tile.building == BuildingType.GENERATOR:
                pygame.draw.rect(surface, GREEN, rect.inflate(-10, -10), border_radius=6)
                draw_arrow(surface, rect, tile.direction)
                draw_building_label(surface, rect, "S")

            elif tile.building == BuildingType.HADAMARD:
                pygame.draw.rect(surface, PURPLE, rect.inflate(-10, -10), border_radius=6)
                draw_arrow(surface, rect, tile.direction)
                draw_building_label(surface, rect, "H")

            elif tile.building == BuildingType.X_GATE:
                pygame.draw.rect(surface, (80, 220, 220), rect.inflate(-10, -10), border_radius=6)
                draw_arrow(surface, rect, tile.direction)
                draw_building_label(surface, rect, "X")

            elif tile.building == BuildingType.MEASUREMENT:
                pygame.draw.rect(surface, (235, 190, 80), rect.inflate(-10, -10), border_radius=6)
                draw_arrow(surface, rect, tile.direction)
                draw_building_label(surface, rect, "M")
                draw_measurement_histogram(surface, rect, tile)

            # Draw item on tile
            if tile.item:
                dx, dy = DIR_VECTORS[tile.direction]

                if tile.building == BuildingType.GENERATOR:
                    px = sx + size / 2
                    py = sy + size / 2
                else:
                    px = sx + size / 2 + dx * tile.item.progress * size * 0.4
                    py = sy + size / 2 + dy * tile.item.progress * size * 0.4

                tile.item.draw(surface, px - 10, py - 10, 20)


def draw_ui(surface, selected_building, selected_rotation, paused):
    """Draw the UI overlay."""
    font = pygame.font.SysFont("consolas", 18)

    lines = [
        "1 = Belt",
        "2 = Generator",
        "3 = Hadamard",
        "4 = X Gate",
        "5 = Measure",
        "R = Rotate",
        "P = Pause",
        "N = Step (paused)",
        "WASD = Move Camera",
        "Mouse Wheel = Zoom",
    ]

    current = f"Selected: {selected_building.name} | Rotation: {selected_rotation.name}"
    status = "PAUSED" if paused else "RUNNING"

    y = 10

    for line in lines:
        text = font.render(line, True, WHITE)
        surface.blit(text, (10, y))
        y += 22

    text = font.render(current, True, YELLOW)
    surface.blit(text, (10, y + 10))

    status_text = font.render(status, True, GREEN if not paused else RED)
    surface.blit(status_text, (10, y + 34))

    # Debug: show mouse tile coordinates
    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my, TILE_SIZE)
    debug_text = font.render(f"Tile: ({wx}, {wy})", True, WHITE)
    debug_rect = debug_text.get_rect(topright=(WIDTH - 10, 10))
    surface.blit(debug_text, debug_rect)
