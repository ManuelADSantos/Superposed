"""Infrastructure buildings: belt, generator, output sink."""

from __future__ import annotations

from ..gate_registry import register, GateDef, Category, BELT, GENERATOR, OUTPUT_SINK



register(GateDef(
    id=BELT,
    name="Belt",
    tip="Transports qubits",
    color=(84, 136, 210),
    category=Category.INFRASTRUCTURE,

    order=10,
))

register(GateDef(
    id=GENERATOR,
    name="Generator",
    tip="Spawns |0⟩ qubits",
    color=(108, 220, 136),
    category=Category.INFRASTRUCTURE,

    order=11,
))

register(GateDef(
    id=OUTPUT_SINK,
    name="Sink",
    tip="Collects output qubits",
    color=(220, 200, 255),
    category=Category.INFRASTRUCTURE,

    order=90,
))
