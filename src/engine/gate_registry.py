"""Central gate registry — single source of truth for all buildings.

To add a gate, create a .py file in gates/ that calls register() with a GateDef.
"""

from __future__ import annotations
import os
import importlib
from dataclasses import dataclass
from typing import Callable


class Category:
    INFRASTRUCTURE = "infrastructure"
    SINGLE = "single"
    TWO_QUBIT = "two_qubit"
    CONSUMER = "consumer"
    ROUTER = "router"


@dataclass
class GateDef:
    id: str
    name: str
    tip: str
    color: tuple
    category: str
    transform: Callable | None = None
    sprite_fn: Callable | None = None
    overlay_fn: Callable | None = None
    order: int = 100


EMPTY = "empty"
BELT = "belt"
GENERATOR = "generator"
OUTPUT_SINK = "output_sink"

GATES: dict[str, GateDef] = {}
_toolbar_cache: list | None = None


def register(gate: GateDef):
    global _toolbar_cache
    GATES[gate.id] = gate
    _toolbar_cache = None


def get_gate(building_id: str) -> GateDef | None:
    return GATES.get(building_id)


def toolbar_order() -> list[GateDef]:
    global _toolbar_cache
    if _toolbar_cache is None:
        _toolbar_cache = sorted(GATES.values(), key=lambda g: g.order)
    return _toolbar_cache


def gate_ids() -> list[str]:
    return [g.id for g in toolbar_order()]


def active_toolbar(available: list[str] | None = None) -> list[str]:
    all_ids = [g.id for g in toolbar_order()]
    if available is not None:
        return [gid for gid in all_ids if gid in available]
    return all_ids


def load_gates():
    """Import every .py in gates/ — each calls register() at module scope."""
    gates_dir = os.path.join(os.path.dirname(__file__), "gates")
    if not os.path.isdir(gates_dir):
        return
    for fname in sorted(os.listdir(gates_dir)):
        if fname.endswith(".py") and not fname.startswith("__"):
            mod_name = f"src.engine.gates.{fname[:-3]}"
            importlib.import_module(mod_name)
