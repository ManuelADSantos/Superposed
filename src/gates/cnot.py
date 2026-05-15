"""CNOT gate — two-qubit entangling gate.

Control enters from CCW perpendicular, target enters from behind.
If control is |1⟩, target is flipped.
If control is superposition, both become entangled.
"""

from gate_registry import register, GateDef, Category


def _transform(control, target):
    """Apply CNOT: flip target if control is |1⟩; entangle if superposition."""
    from entities import QubitState
    from world import create_entangle_group, register_entangled

    if control.state == QubitState.ONE:
        # Flip target
        if target.state == QubitState.ZERO:
            target.state = QubitState.ONE
        elif target.state == QubitState.ONE:
            target.state = QubitState.ZERO
    elif control.state == QubitState.SUPERPOSITION:
        if target.state in (QubitState.ZERO, QubitState.ONE):
            target.state = QubitState.SUPERPOSITION
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)


def _sprite(d, size):
    import pygame
    from sprites import _surf, _panel, _dir_mark, _a
    from config import WHITE, GOLD
    from entities import DIR_VECTORS, ccw_dir, cw_dir, opposite_dir
    COLOR = (255, 180, 80)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (100, 70, 30), COLOR, 10)
    pygame.draw.line(s, _a(WHITE, 140), (b.centerx, b.top + 8), (b.centerx, b.bottom - 8), 2)
    pygame.draw.line(s, _a(WHITE, 140), (b.left + 8, b.centery), (b.right - 8, b.centery), 2)
    r_dot = max(4, int(size * 0.08))
    ctrl_offset = int(size * 0.18)
    cdx, cdy = DIR_VECTORS[ccw_dir(d)]
    dot_x = b.centerx + cdx * ctrl_offset
    dot_y = b.centery + cdy * ctrl_offset
    pygame.draw.circle(s, GOLD, (dot_x, dot_y), r_dot)
    tdx, tdy = DIR_VECTORS[opposite_dir(d)]
    targ_x = b.centerx + tdx * ctrl_offset
    targ_y = b.centery + tdy * ctrl_offset
    r_targ = max(5, int(size * 0.12))
    pygame.draw.circle(s, _a(WHITE, 200), (targ_x, targ_y), r_targ, 2)
    pygame.draw.line(s, _a(WHITE, 200), (targ_x - r_targ, targ_y), (targ_x + r_targ, targ_y), 2)
    pygame.draw.line(s, _a(WHITE, 200), (targ_x, targ_y - r_targ), (targ_x, targ_y + r_targ), 2)
    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="cnot",
    name="CNOT",
    tip="Entangles two qubits",
    color=(255, 180, 80),
    category=Category.TWO_QUBIT,
    transform=_transform,
    sprite_fn=_sprite,
    order=30,
))
