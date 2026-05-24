"""Infrastructure buildings: belt, generator, output sink.

These have hardcoded simulation behaviour but are registered here so that
the toolbar, sprites, and levels all pick them up automatically.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category, BELT, GENERATOR, OUTPUT_SINK


# ── Sprite helpers (lazy-imported to avoid pygame at parse time) ──────────

def _belt_sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _arrow, _shine, _a
    from ...core.config import WHITE
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (36, 60, 95), (84, 136, 210), 10)
    inner = b.inflate(-10, -10)
    pygame.draw.rect(s, (20, 32, 50), inner, border_radius=7)
    pygame.draw.rect(s, _a((84, 136, 210), 160), inner, 2, border_radius=7)
    _dir_mark(s, d, b, (165, 210, 255))
    _arrow(s, b.centerx, b.centery, d, _a(WHITE, 140), length=int(size * 0.18))
    _shine(s, size)
    return s


def _generator_sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _shine, _a
    from ...core.config import WHITE
    COLOR = (108, 220, 136)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (28, 75, 52), COLOR, 10)
    r = int(size * 0.2)
    pygame.draw.circle(s, (70, 255, 150), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 100), b.center, r, 2)
    pygame.draw.circle(s, _a(COLOR, 80), b.center, r + 6, 2)
    _dir_mark(s, d, b, (180, 255, 210))
    _shine(s, size)
    return s


def _sink_sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a
    from ...core.config import WHITE
    COLOR = (220, 200, 255)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (55, 45, 90), COLOR, 10)
    r = int(size * 0.22)
    pygame.draw.circle(s, _a(COLOR, 180), b.center, r)
    pygame.draw.circle(s, _a(WHITE, 120), b.center, r, 2)
    pygame.draw.polygon(s, _a(WHITE, 160), [
        (b.centerx, b.centery + 4),
        (b.centerx - 6, b.centery - 4),
        (b.centerx + 6, b.centery - 4),
    ])
    _dir_mark(s, d, b, COLOR)
    return s


# ── Registration ─────────────────────────────────────────────────────────

register(GateDef(
    id=BELT,
    name="Belt",
    tip="Transports qubits",
    color=(84, 136, 210),
    category=Category.INFRASTRUCTURE,
    sprite_fn=_belt_sprite,
    order=10,
))

register(GateDef(
    id=GENERATOR,
    name="Generator",
    tip="Spawns |0⟩ qubits",
    color=(108, 220, 136),
    category=Category.INFRASTRUCTURE,
    sprite_fn=_generator_sprite,
    order=11,
))

register(GateDef(
    id=OUTPUT_SINK,
    name="Sink",
    tip="Collects output qubits",
    color=(220, 200, 255),
    category=Category.INFRASTRUCTURE,
    sprite_fn=_sink_sprite,
    order=90,
))
