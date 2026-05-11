"""Sprite generation and caching for entities."""

from functools import lru_cache

import pygame

from config import RED, BLUE, PURPLE, WHITE, YELLOW
from entities import BuildingType, QubitState, Direction


def _with_alpha(color, alpha):
    return (*color[:3], alpha)


def _make_surface(size):
    return pygame.Surface((size, size), pygame.SRCALPHA)


def _draw_shadow(surface, rect, radius):
    shadow_rect = rect.move(2, 3)
    pygame.draw.rect(surface, (0, 0, 0, 90), shadow_rect, border_radius=radius)


def _draw_panel(surface, rect, base_color, border_color, radius=10):
    pygame.draw.rect(surface, _with_alpha(base_color, 255), rect, border_radius=radius)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=radius)


def _direction_edge(rect, direction):
    if direction == Direction.UP:
        return pygame.Rect(rect.left + 10, rect.top + 8, rect.width - 20, 10)
    if direction == Direction.RIGHT:
        return pygame.Rect(rect.right - 18, rect.top + 10, 10, rect.height - 20)
    if direction == Direction.DOWN:
        return pygame.Rect(rect.left + 10, rect.bottom - 18, rect.width - 20, 10)
    return pygame.Rect(rect.left + 8, rect.top + 10, 10, rect.height - 20)


def _draw_direction_mark(surface, direction, rect, accent_color):
    edge = _direction_edge(rect, direction)
    glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(glow, _with_alpha(accent_color, 120), edge, border_radius=4)
    surface.blit(glow, (0, 0))


def _draw_belt(surface, direction, size):
    sprite = _make_surface(size)
    base = pygame.Rect(5, 5, size - 10, size - 10)
    _draw_shadow(sprite, base, 12)
    _draw_panel(sprite, base, (40, 66, 100), (84, 136, 210), radius=12)

    inner = base.inflate(-12, -12)
    pygame.draw.rect(sprite, (22, 34, 50), inner, border_radius=9)
    pygame.draw.rect(sprite, (68, 112, 180), inner, 2, border_radius=9)

    _draw_direction_mark(sprite, direction, base, (165, 210, 255))

    shine = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.line(shine, (255, 255, 255, 45), (8, 8), (size - 10, 10), 3)
    sprite.blit(shine, (0, 0))
    return sprite


def _draw_generator(surface, direction, size):
    sprite = _make_surface(size)
    base = pygame.Rect(5, 5, size - 10, size - 10)
    _draw_shadow(sprite, base, 12)
    _draw_panel(sprite, base, (30, 82, 58), (108, 220, 136), radius=12)

    core_size = int(size * 0.4)
    core = pygame.Rect(base.centerx - core_size // 2, base.centery - core_size // 2, core_size, core_size)
    pygame.draw.ellipse(sprite, (70, 255, 150), core)
    pygame.draw.ellipse(sprite, (220, 255, 235), core.inflate(-10, -10), 2)

    ring = core.inflate(16, 16)
    pygame.draw.ellipse(sprite, (170, 255, 205, 120), ring, 3)
    _draw_direction_mark(sprite, direction, base, (180, 255, 210))

    return sprite


def _draw_hadamard(surface, direction, size):
    sprite = _make_surface(size)
    base = pygame.Rect(5, 5, size - 10, size - 10)
    _draw_shadow(sprite, base, 12)
    _draw_panel(sprite, base, (72, 38, 126), (190, 135, 255), radius=12)

    crystal = [
        (base.centerx, base.top + 8),
        (base.right - 10, base.centery),
        (base.centerx, base.bottom - 8),
        (base.left + 10, base.centery),
    ]
    pygame.draw.polygon(sprite, (205, 165, 255), crystal)
    pygame.draw.polygon(sprite, (255, 245, 255), crystal, 2)

    font = pygame.font.SysFont("consolas", max(14, int(size * 0.33)), bold=True)
    text = font.render("H", True, WHITE)
    sprite.blit(text, text.get_rect(center=base.center))

    _draw_direction_mark(sprite, direction, base, (220, 185, 255))
    return sprite


def _draw_x_gate(surface, direction, size):
    sprite = _make_surface(size)
    base = pygame.Rect(5, 5, size - 10, size - 10)
    _draw_shadow(sprite, base, 12)
    _draw_panel(sprite, base, (26, 86, 90), (115, 240, 240), radius=12)

    inset = base.inflate(-18, -18)
    pygame.draw.line(sprite, (225, 255, 255), inset.topleft, inset.bottomright, 6)
    pygame.draw.line(sprite, (225, 255, 255), inset.topright, inset.bottomleft, 6)
    pygame.draw.line(sprite, (120, 255, 255), inset.topleft, inset.bottomright, 2)
    pygame.draw.line(sprite, (120, 255, 255), inset.topright, inset.bottomleft, 2)

    _draw_direction_mark(sprite, direction, base, (150, 250, 255))
    return sprite


def _draw_measurement(surface, direction, size):
    sprite = _make_surface(size)
    base = pygame.Rect(5, 5, size - 10, size - 10)
    _draw_shadow(sprite, base, 12)
    _draw_panel(sprite, base, (95, 70, 22), (255, 214, 112), radius=12)

    lens = pygame.Rect(0, 0, int(size * 0.44), int(size * 0.44))
    lens.center = base.center
    pygame.draw.ellipse(sprite, (255, 236, 180), lens)
    pygame.draw.ellipse(sprite, (255, 255, 255), lens.inflate(-10, -10), 2)

    meter = pygame.Rect(0, 0, int(size * 0.58), int(size * 0.18))
    meter.center = (base.centerx, base.bottom - 18)
    pygame.draw.rect(sprite, (44, 34, 20), meter, border_radius=8)
    pygame.draw.rect(sprite, (255, 220, 120), meter, 2, border_radius=8)
    pygame.draw.line(sprite, RED, (meter.left + 8, meter.centery), (meter.centerx - 2, meter.centery), 4)
    pygame.draw.line(sprite, BLUE, (meter.centerx + 2, meter.centery), (meter.right - 8, meter.centery), 4)

    _draw_direction_mark(sprite, direction, base, (255, 225, 145))
    return sprite


def _draw_qubit_surface(state, size, disappearing=False, progress=1.0):
    sprite = _make_surface(size)
    cx = size / 2
    cy = size / 2

    if disappearing:
        size_scale = max(0.18, progress)
        radius = max(2, int(size * 0.28 * size_scale))
        glow_radius = max(radius + 4, int(radius * 1.8))
    else:
        radius = max(3, int(size * 0.28))
        glow_radius = int(radius * 1.8)

    if state == QubitState.SUPERPOSITION:
        base_color = PURPLE
    elif state == QubitState.ZERO:
        base_color = RED
    else:
        base_color = BLUE

    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(glow, _with_alpha(base_color, 70), (int(cx), int(cy)), glow_radius)
    sprite.blit(glow, (0, 0))

    pygame.draw.circle(sprite, _with_alpha(base_color, 255), (int(cx), int(cy)), radius)
    pygame.draw.circle(sprite, _with_alpha(WHITE, 120), (int(cx - radius * 0.28), int(cy - radius * 0.28)), max(1, radius // 2))

    if state == QubitState.SUPERPOSITION:
        pygame.draw.circle(sprite, WHITE, (int(cx), int(cy)), radius + 1, 2)
        pygame.draw.circle(sprite, _with_alpha(YELLOW, 180), (int(cx), int(cy)), max(2, radius // 2), 1)
    else:
        pygame.draw.circle(sprite, WHITE, (int(cx), int(cy)), radius + 1, 1)

    return sprite


@lru_cache(maxsize=256)
def get_building_sprite(building, direction, size):
    if building == BuildingType.BELT:
        return _draw_belt(None, direction, size)
    if building == BuildingType.GENERATOR:
        return _draw_generator(None, direction, size)
    if building == BuildingType.HADAMARD:
        return _draw_hadamard(None, direction, size)
    if building == BuildingType.X_GATE:
        return _draw_x_gate(None, direction, size)
    if building == BuildingType.MEASUREMENT:
        return _draw_measurement(None, direction, size)
    return None


@lru_cache(maxsize=256)
def get_qubit_sprite(state, size, disappearing=False, progress=1.0):
    return _draw_qubit_surface(state, size, disappearing=disappearing, progress=progress)