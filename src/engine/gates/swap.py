"""SWAP gate — exchanges the quantum states of two qubits.

After a SWAP, each qubit carries the other's original state (and phase).
Useful for crossing qubit streams and rerouting without changing states.

  SWAP(|a>, |b>) = (|b>, |a>)

Uses the same two-input geometry as CNOT:
  Target  enters from behind (opposite of facing direction).
  "Control" enters from the CCW-perpendicular side.
Both labels are symmetric — SWAP doesn't distinguish them by role.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(control, target):
    """Swap quantum states between the two qubits."""
    from ...core.world import break_entanglement
    # Exchange states and phases
    control.state, target.state = target.state, control.state
    control.phase_flipped, target.phase_flipped = (
        target.phase_flipped, control.phase_flipped
    )
    # Break entanglement — each qubit is now in a new stream context
    break_entanglement(control)
    break_entanglement(target)


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a, _arrow
    from ...core.config import WHITE
    from ...core.entities import DIR_VECTORS, ccw_dir, cw_dir, opposite_dir
    COLOR = (255, 140, 60)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (100, 50, 18), COLOR, 10)

    # Two crossing ×-style arrows showing exchange
    cx, cy = b.centerx, b.centery
    off = int(size * 0.17)
    lw = max(2, int(size * 0.05))

    # Arrow 1: comes from back direction, exits CW direction
    back_dx, back_dy = DIR_VECTORS[opposite_dir(d)]
    cw_dx, cw_dy = DIR_VECTORS[cw_dir(d)]
    p1s = (cx + back_dx * off, cy + back_dy * off)
    p1e = (cx + cw_dx * off,  cy + cw_dy * off)
    pygame.draw.line(s, _a(WHITE, 200), p1s, p1e, lw)
    # arrowhead at p1e
    _arrow(s, cx, cy, cw_dir(d), _a(WHITE, 200), off, lw)

    # Arrow 2: comes from CCW direction, exits forward direction
    ccw_dx, ccw_dy = DIR_VECTORS[ccw_dir(d)]
    fwd_dx, fwd_dy = DIR_VECTORS[d]
    p2s = (cx + ccw_dx * off, cy + ccw_dy * off)
    p2e = (cx + fwd_dx * off, cy + fwd_dy * off)
    pygame.draw.line(s, _a(COLOR, 230), p2s, p2e, lw)
    _arrow(s, cx, cy, d, _a(COLOR, 230), off, lw)

    # Centre ×
    r = max(4, int(size * 0.09))
    pygame.draw.line(s, _a(WHITE, 180), (cx - r, cy - r), (cx + r, cy + r), lw + 1)
    pygame.draw.line(s, _a(WHITE, 180), (cx + r, cy - r), (cx - r, cy + r), lw + 1)

    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="swap",
    name="SWAP",
    tip="Exchanges two qubit states",
    color=(255, 140, 60),
    category=Category.TWO_QUBIT,
    transform=_transform,
    sprite_fn=_sprite,
    order=32,
))
