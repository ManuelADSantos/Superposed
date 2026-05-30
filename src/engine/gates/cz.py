"""CZ gate — Controlled-Z.

Applies Z to the target when control is |1>.
Because Z only affects phase, the most visible effect is on superposition.

Key behaviours:
  control=|1>,  target=|+>  →  target becomes |->  (phase flip)
  control=|+>,  target=|1>  →  control becomes |->  (phase kickback!)
  control=|+>,  target=|+>  →  entangled Bell-like state
  control=|0>               →  nothing happens (Z|anything> when c=0 = identity)

Unlike CNOT (which flips bits), CZ flips phases — all its effects are invisible
on pure |0>/|1> states and only show up through interference.

Control enters from the CCW-perpendicular side (same convention as CNOT).
Target enters from behind.
"""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category


def _transform(control, target):
    from ...core.entities import QubitState
    from ...core.world import create_entangle_group, register_entangled

    if control.state == QubitState.ONE:
        # Apply Z to target: only visible on superposition
        if target.state == QubitState.SUPERPOSITION:
            target.phase_flipped = not target.phase_flipped
        # |0> and |1> are eigenstates of Z — no effect

    elif control.state == QubitState.SUPERPOSITION:
        if target.state == QubitState.ONE:
            # Phase kickback: Z kicks back onto the control qubit's phase
            control.phase_flipped = not control.phase_flipped
        elif target.state == QubitState.SUPERPOSITION:
            # Both in superposition → entangle
            gid = create_entangle_group()
            register_entangled(gid, control)
            register_entangled(gid, target)
        # target=|0>: Z|0>=|0>, no effect on control either


def _sprite(d, size):
    import pygame
    from ...ui.sprites import _surf, _panel, _dir_mark, _a
    from ...core.config import WHITE, GOLD
    from ...core.entities import DIR_VECTORS, ccw_dir, opposite_dir
    COLOR = (80, 180, 255)
    s = _surf(size)
    b = pygame.Rect(4, 4, size - 8, size - 8)
    _panel(s, b, (20, 55, 100), COLOR, 10)

    # Cross-hairs
    pygame.draw.line(s, _a(WHITE, 100),
                     (b.centerx, b.top + 8), (b.centerx, b.bottom - 8), 2)
    pygame.draw.line(s, _a(WHITE, 100),
                     (b.left + 8, b.centery), (b.right - 8, b.centery), 2)

    ctrl_offset = int(size * 0.18)
    label_offset = int(size * 0.35)
    font_size = max(8, int(size * 0.18))
    lf = pygame.font.SysFont("consolas", font_size, bold=True)

    # Control dot on CCW side
    r_dot = max(4, int(size * 0.08))
    cdx, cdy = DIR_VECTORS[ccw_dir(d)]
    dot_x = b.centerx + cdx * ctrl_offset
    dot_y = b.centery + cdy * ctrl_offset
    pygame.draw.circle(s, GOLD, (dot_x, dot_y), r_dot)
    c_lbl = lf.render("C", True, GOLD)
    s.blit(c_lbl, c_lbl.get_rect(center=(
        b.centerx + cdx * label_offset,
        b.centery + cdy * label_offset,
    )))

    # Target side: "Z" label (phase flip symbol) instead of CNOT's ⊕
    tdx, tdy = DIR_VECTORS[opposite_dir(d)]
    tz_x = b.centerx + tdx * ctrl_offset
    tz_y = b.centery + tdy * ctrl_offset
    font_z = pygame.font.SysFont("consolas", max(10, int(size * 0.24)), bold=True)
    z_lbl = font_z.render("Z", True, _a(COLOR, 230))
    s.blit(z_lbl, z_lbl.get_rect(center=(tz_x, tz_y)))
    t_lbl = lf.render("T", True, _a(WHITE, 180))
    s.blit(t_lbl, t_lbl.get_rect(center=(
        b.centerx + tdx * label_offset,
        b.centery + tdy * label_offset,
    )))

    _dir_mark(s, d, b, COLOR)
    return s


register(GateDef(
    id="cz",
    name="CZ Gate",
    tip="Controlled phase flip (C=control, T=target)",
    color=(80, 180, 255),
    category=Category.TWO_QUBIT,
    transform=_transform,
    sprite_fn=_sprite,
    order=31,
))
