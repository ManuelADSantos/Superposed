"""Noise gate — randomly corrupts qubits (50% bit flip)."""

from __future__ import annotations

import random
from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if random.random() < 0.5:
        if item.state == QubitState.ZERO:
            item.state = QubitState.ONE
        elif item.state == QubitState.ONE:
            item.state = QubitState.ZERO
        elif item.state == QubitState.SUPERPOSITION:
            item.phase_flipped = not item.phase_flipped


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a
    from ...core.config import WHITE
    COLOR = (200, 70, 70)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (90, 30, 30), COLOR, 10)
    font = pygame.font.SysFont("consolas", max(12, int(size * 0.28)), bold=True)
    txt = font.render("N", True, WHITE)
    s.blit(txt, txt.get_rect(center=(b.centerx, b.centery - 2)))
    # Static/interference lines
    for i in range(3):
        y = b.top + 12 + i * int((b.height - 24) / 2)
        pts = []
        for x in range(b.left + 8, b.right - 8, 6):
            jitter = random.randint(-3, 3)
            pts.append((x, y + jitter))
        if len(pts) > 1:
            pygame.draw.lines(s, _a(WHITE, 80), False, pts, 1)
    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="noise",
    name="Noise",
    tip="Random corruption",
    color=(200, 70, 70),
    category=Category.SINGLE,
    transform=_transform,
    sprite_fn=_sprite,
    order=60,
))
