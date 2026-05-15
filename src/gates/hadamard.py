"""Hadamard gate — creates superposition.

H|0⟩ = |+⟩,  H|1⟩ = |−⟩,  H|+⟩ = |0⟩,  H|−⟩ = |1⟩
"""

from gate_registry import register, GateDef, Category


def _transform(item):
    from entities import QubitState
    from world import break_entanglement
    if item.state in (QubitState.ZERO, QubitState.ONE):
        item.phase_flipped = (item.state == QubitState.ONE)
        item.state = QubitState.SUPERPOSITION
    else:
        if item.phase_flipped:
            item.state = QubitState.ONE
        else:
            item.state = QubitState.ZERO
        item.phase_flipped = False
        break_entanglement(item)


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _a
    from config import WHITE
    COLOR = (190, 135, 255)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (65, 34, 115), COLOR, 10)
    diamond = [
        (b.centerx, b.top + 8), (b.right - 10, b.centery),
        (b.centerx, b.bottom - 8), (b.left + 10, b.centery),
    ]
    pygame.draw.polygon(s, (200, 160, 255), diamond)
    pygame.draw.polygon(s, _a(WHITE, 180), diamond, 2)
    font = pygame.font.SysFont("consolas", max(12, int(size * 0.3)), bold=True)
    txt = font.render("H", True, WHITE)
    s.blit(txt, txt.get_rect(center=b.center))
    _dir_mark(s, d, b, (220, 185, 255))
    return s


register(GateDef(
    id="hadamard",
    name="Hadamard",
    tip="Creates superposition",
    color=(190, 135, 255),
    category=Category.SINGLE,
    transform=_transform,
    sprite_fn=_sprite,
    order=20,
))
