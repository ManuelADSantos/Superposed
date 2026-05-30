"""Y gate — Pauli Y.

Y = iXZ: flips |0>↔|1> like X, AND flips the phase like Z.
  Y|0> = |1>
  Y|1> = |0>
  Y|+> = |->   (toggles phase_flipped on superposition)
  Y|-> = |+>
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(item):
    from ...core.entities import QubitState
    if item.state == QubitState.ZERO:
        item.state = QubitState.ONE
    elif item.state == QubitState.ONE:
        item.state = QubitState.ZERO
    else:  # SUPERPOSITION
        item.phase_flipped = not item.phase_flipped


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a
    from ...core.config import WHITE
    COLOR = (100, 220, 100)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (28, 78, 28), COLOR, 10)

    # Y-shape: two upper arms + one vertical stem
    cx, cy = b.centerx, b.centery
    arm = int(size * 0.20)
    stem = int(size * 0.18)
    lw = max(3, int(size * 0.07))
    mid_y = cy - int(size * 0.04)
    # Left arm
    pygame.draw.line(s, _a(WHITE, 210),
                     (cx - arm, cy - arm), (cx, mid_y), lw)
    # Right arm
    pygame.draw.line(s, _a(WHITE, 210),
                     (cx + arm, cy - arm), (cx, mid_y), lw)
    # Stem
    pygame.draw.line(s, _a(WHITE, 210),
                     (cx, mid_y), (cx, cy + stem), lw)
    # Small phase-flip indicator (a tiny circle, like Z gate)
    pygame.draw.circle(s, _a(COLOR, 140), (cx, cy + stem + 4),
                       max(2, int(size * 0.06)), 1)
    _dir_mark(s, d, b, (150, 255, 150))
    return s


register(GateDef(
    id="y_gate",
    name="Y Gate",
    tip="Flips |0>↔|1> + phase flip",
    color=(100, 220, 100),
    category=Category.SINGLE,
    transform=_transform,
    sprite_fn=_sprite,
    order=23,
))
