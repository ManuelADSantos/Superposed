"""X (NOT) gate — flips |0⟩ ↔ |1⟩."""

from gate_registry import register, GateDef, Category


def _transform(item):
    from entities import QubitState
    if item.state == QubitState.ZERO:
        item.state = QubitState.ONE
    elif item.state == QubitState.ONE:
        item.state = QubitState.ZERO


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _a
    from config import WHITE, CYAN
    COLOR = (115, 240, 240)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (24, 80, 85), COLOR, 10)
    ins = b.inflate(-16, -16)
    pygame.draw.line(s, _a(WHITE, 200), ins.topleft, ins.bottomright, 5)
    pygame.draw.line(s, _a(WHITE, 200), ins.topright, ins.bottomleft, 5)
    pygame.draw.line(s, CYAN, ins.topleft, ins.bottomright, 2)
    pygame.draw.line(s, CYAN, ins.topright, ins.bottomleft, 2)
    _dir_mark(s, d, b, (150, 250, 255))
    return s


register(GateDef(
    id="x_gate",
    name="X Gate",
    tip="Flips |0⟩↔|1⟩",
    color=(115, 240, 240),
    category=Category.SINGLE,
    transform=_transform,
    sprite_fn=_sprite,
    order=21,
))
