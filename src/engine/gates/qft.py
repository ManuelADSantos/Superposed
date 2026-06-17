"""Two-qubit QFT block."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category

_S = 1 / 2
_QFT2 = (
    (_S, _S, _S, _S),
    (_S, 1j * _S, -_S, -1j * _S),
    (_S, -_S, _S, -_S),
    (_S, -1j * _S, -_S, 1j * _S),
)


def _transform(control, target):
    from ...core.world import apply_two
    apply_two(control, target, _QFT2)


register(GateDef(
    id="qft",
    name="QFT",
    tip="Two-qubit Fourier transform",
    color=(120, 210, 255),
    category=Category.TWO_QUBIT,
    transform=_transform,
    qubits=2,
    order=34,
))
