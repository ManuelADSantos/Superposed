"""Z gate — phase flip.  |+⟩ ↔ |−⟩ (invisible on basis states)."""

from __future__ import annotations

from gate_registry import register, GateDef, Category


def _transform(item):
    from entities import QubitState
    if item.state == QubitState.SUPERPOSITION:
        item.phase_flipped = not item.phase_flipped


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _a
    from config import WHITE, PINK
    COLOR = (240, 120, 180)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (100, 45, 80), COLOR, 10)
    font = pygame.font.SysFont("consolas", max(12, int(size * 0.34)), bold=True)
    txt = font.render("Z", True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    pygame.draw.circle(s, _a(PINK, 100), b.center, int(size * 0.24), 2)
    _dir_mark(s, d, b, PINK)
    return s


register(GateDef(
    id="z_gate",
    name="Z Gate",
    tip="Phase flip",
    color=(240, 120, 180),
    category=Category.SINGLE,
    transform=_transform,
    sprite_fn=_sprite,
    order=22,
))
