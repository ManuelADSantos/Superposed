"""Measurement gate — collapses superposition probabilistically.

This is a CONSUMER: the qubit is absorbed and a histogram is updated.
"""

import random
from gate_registry import register, GateDef, Category


def _transform(item, tile):
    """Measure the qubit, collapse entangled partners, update histogram."""
    from entities import QubitState
    from world import get_entangled_partners, break_entanglement

    if item.state == QubitState.SUPERPOSITION:
        result = random.choice([QubitState.ZERO, QubitState.ONE])
        item.state = result
        item.phase_flipped = False
        for partner in get_entangled_partners(item):
            if partner.state == QubitState.SUPERPOSITION:
                partner.state = result
                partner.phase_flipped = False
            break_entanglement(partner)
        break_entanglement(item)

    # Record on the tile's histogram
    tile.measurements.append(item.state)
    if len(tile.measurements) > 20:
        tile.measurements.pop(0)
    tile.measure_flash = 0.35


def _overlay(surface, rect, tile):
    """Draw histogram and timeline on the measurement tile."""
    import pygame
    from config import WHITE, RED, BLUE
    from entities import QubitState, state_color

    if not tile.measurements:
        return
    chart = rect.inflate(-14, -22)
    chart.height = max(14, chart.height // 2)
    chart.top = rect.top + 6
    zero_n = sum(1 for o in tile.measurements if o == QubitState.ZERO)
    one_n = sum(1 for o in tile.measurements if o == QubitState.ONE)
    total = max(1, zero_n + one_n)
    gap = 4
    bw = max(3, (chart.width - gap) // 2)
    mh = chart.height - 4
    rh = max(3, int(mh * zero_n / total))
    bh = max(3, int(mh * one_n / total))
    pygame.draw.rect(surface, RED, pygame.Rect(chart.left, chart.bottom - rh, bw, rh))
    pygame.draw.rect(surface, BLUE, pygame.Rect(chart.left + bw + gap, chart.bottom - bh, bw, bh))
    pygame.draw.rect(surface, WHITE, chart, 1)
    ty = chart.bottom + 2
    tw = max(2, chart.width // 20)
    for i, o in enumerate(tile.measurements[-20:]):
        tr = pygame.Rect(chart.left + i * tw, ty, tw - 1, 3)
        pygame.draw.rect(surface, state_color(o), tr)
    if tile.measure_flash > 0:
        alpha = int(160 * min(tile.measure_flash / 0.35, 1.0))
        fs = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fs, (255, 255, 255, alpha), fs.get_rect(), 3, border_radius=6)
        surface.blit(fs, rect.topleft)


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _a
    from config import WHITE, RED, BLUE
    COLOR = (255, 214, 112)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (90, 65, 20), COLOR, 10)
    r = int(size * 0.2)
    pygame.draw.circle(s, (255, 236, 180), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 140), b.center, r, 2)
    pygame.draw.circle(s, (90, 65, 20), b.center, max(3, r // 2))
    meter = pygame.Rect(0, 0, int(size * 0.54), int(size * 0.14))
    meter.center = (b.centerx, b.bottom - 14)
    pygame.draw.rect(s, (40, 30, 18), meter, border_radius=6)
    pygame.draw.rect(s, _a(COLOR, 180), meter, 2, border_radius=6)
    pygame.draw.line(s, RED, (meter.left + 6, meter.centery), (meter.centerx - 2, meter.centery), 3)
    pygame.draw.line(s, BLUE, (meter.centerx + 2, meter.centery), (meter.right - 6, meter.centery), 3)
    _dir_mark(s, d, b, (255, 225, 145))
    return s


register(GateDef(
    id="measurement",
    name="Measure",
    tip="Collapses superposition",
    color=(255, 214, 112),
    category=Category.CONSUMER,
    transform=_transform,
    sprite_fn=_sprite,
    overlay_fn=_overlay,
    order=40,
))
