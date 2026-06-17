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
    # ponytail: colors matched to pixel-art sprite, coords proportional to tile size
    SRED, SBLU = (220, 80, 80), (100, 160, 255)
    s = rect.width / 64
    chart = pygame.Rect(
        rect.left + int(15 * s), rect.top + int(14 * s),
        int(34 * s), int(30 * s))
    zero_n = sum(1 for o in tile.measurements if o == QubitState.ZERO)
    one_n = sum(1 for o in tile.measurements if o == QubitState.ONE)
    total = max(1, zero_n + one_n)
    gap = max(2, int(3 * s))
    bw = max(3, (chart.width - gap) // 2)
    mh = chart.height - 2
    rh = max(3, int(mh * zero_n / total))
    bh = max(3, int(mh * one_n / total))
    pygame.draw.rect(surface, SRED, pygame.Rect(chart.left, chart.bottom - rh, bw, rh))
    pygame.draw.rect(surface, SBLU, pygame.Rect(chart.left + bw + gap, chart.bottom - bh, bw, bh))
    ty = rect.top + int(49 * s)
    tw = max(2, chart.width // 20)
    for i, o in enumerate(tile.measurements[-20:]):
        tr = pygame.Rect(chart.left + i * tw, ty, tw - 1, 3)
        pygame.draw.rect(surface, state_color(o), tr)
    if tile.measure_flash > 0:
        alpha = int(160 * min(tile.measure_flash / 0.35, 1.0))
        fs = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fs, (255, 255, 255, alpha), fs.get_rect(), 3, border_radius=6)
        surface.blit(fs, rect.topleft)


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
