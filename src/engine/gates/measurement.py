"""Measurement gate — collapses superposition probabilistically.

This is a CONSUMER: the qubit is absorbed and a histogram is updated.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item, tile):
    """Measure the qubit, collapse entangled partners, update histogram."""
    from ...core.world import measure_qubit
    result = measure_qubit(item)
    tile.measurements.append(result)
    if len(tile.measurements) > 20:
        tile.measurements.pop(0)
    tile.measure_flash = 0.35


def _overlay(surface, rect, tile):
    """Draw histogram and timeline on the measurement tile."""
    import pygame
    from ...core.entities import QubitState, state_color

    if not tile.measurements:
        return
    ZERO_COLOR, ONE_COLOR = (220, 80, 80), (100, 160, 255)
    scale = rect.width / 64
    chart_area = pygame.Rect(
        rect.left + int(15 * scale), rect.top + int(14 * scale),
        int(35 * scale), int(34 * scale))
    zero_count = sum(1 for m in tile.measurements if m == QubitState.ZERO)
    one_count = sum(1 for m in tile.measurements if m == QubitState.ONE)
    total_count = max(1, zero_count + one_count)
    bar_gap = max(2, int(2 * scale))
    bar_width = max(3, (chart_area.width - bar_gap) // 2)
    max_bar_height = chart_area.height - 2
    zero_bar_height = max(3, int(max_bar_height * zero_count / total_count))
    one_bar_height = max(3, int(max_bar_height * one_count / total_count))
    pygame.draw.rect(surface, ZERO_COLOR, pygame.Rect(
        chart_area.left, chart_area.bottom - zero_bar_height, bar_width, zero_bar_height))
    pygame.draw.rect(surface, ONE_COLOR, pygame.Rect(
        chart_area.left + bar_width + bar_gap, chart_area.bottom - one_bar_height, bar_width, one_bar_height))
    timeline_y = rect.top + int(50 * scale)
    recent = tile.measurements[-20:]
    n = len(recent)
    tick_height = max(1, int(3 * scale))
    tick_gap = max(1, int(scale))
    for i, outcome in enumerate(recent):
        x0 = chart_area.left + chart_area.width * i // n
        x1 = chart_area.left + chart_area.width * (i + 1) // n
        pygame.draw.rect(surface, state_color(outcome),
                         pygame.Rect(x0, timeline_y, max(1, x1 - x0 - tick_gap), tick_height))
    if tile.measure_flash > 0:
        flash_alpha = int(160 * min(tile.measure_flash / 0.35, 1.0))
        flash_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(flash_surface, (255, 255, 255, flash_alpha), flash_surface.get_rect(), 3, border_radius=6)
        surface.blit(flash_surface, rect.topleft)


register(GateDef(
    id="measurement",
    name="Measure",
    tip="Collapses superposition",
    color=(255, 214, 112),
    category=Category.CONSUMER,
    transform=_transform,

    overlay_fn=_overlay,
    order=40,
))
