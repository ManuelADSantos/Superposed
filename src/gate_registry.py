"""Central gate registry — the single source of truth for all buildings.

To add a new gate, create a .py file in the gates/ folder that calls
register() with a GateDef.  Everything else (toolbar, sprites, simulation,
levels) reads from this registry automatically.
"""

from __future__ import annotations
import os
import importlib
from dataclasses import dataclass, field
from typing import Callable, Optional


# ── Gate categories (controls how simulation handles the building) ────────
class Category:
    INFRASTRUCTURE = "infrastructure"   # belt, generator, sink — hardcoded sim
    SINGLE = "single"                   # 1-qubit gate: transform(item)
    TWO_QUBIT = "two_qubit"             # 2-qubit gate: transform(control, target)
    CONSUMER = "consumer"               # eats the qubit: transform(item, tile)
    ROUTER = "router"                   # routes qubit: transform(x, y, tile, item, eject_fn)


# ── Gate definition ──────────────────────────────────────────────────────
@dataclass
class GateDef:
    id: str                                 # unique string key, e.g. "hadamard"
    name: str                               # display name, e.g. "Hadamard"
    tip: str                                # tooltip, e.g. "Creates superposition"
    color: tuple                            # (R, G, B) accent colour
    category: str                           # one of Category.*

    # --- behaviour ---
    transform: Optional[Callable] = None    # see Category for signature

    # --- visuals ---
    sprite_fn: Optional[Callable] = None    # (direction, size) -> pygame.Surface
    overlay_fn: Optional[Callable] = None   # (surface, rect, tile) -> None

    # --- ordering ---
    order: int = 100                        # lower = further left in toolbar


# ── Well-known IDs (infrastructure) ──────────────────────────────────────
EMPTY = "empty"
BELT = "belt"
GENERATOR = "generator"
OUTPUT_SINK = "output_sink"

# ── The registry ─────────────────────────────────────────────────────────
GATES: dict[str, GateDef] = {}
_toolbar_cache: Optional[list] = None


def register(gate: GateDef):
    """Register a gate definition.  Duplicates overwrite silently."""
    global _toolbar_cache
    GATES[gate.id] = gate
    _toolbar_cache = None


def get_gate(building_id: str) -> Optional[GateDef]:
    """Look up a gate by its string id.  Returns None for EMPTY / unknown."""
    return GATES.get(building_id)


def toolbar_order() -> list[GateDef]:
    """All registered buildings sorted by their toolbar order."""
    global _toolbar_cache
    if _toolbar_cache is None:
        _toolbar_cache = sorted(GATES.values(), key=lambda g: g.order)
    return _toolbar_cache


def gate_ids() -> list[str]:
    """All registered gate IDs in toolbar order."""
    return [g.id for g in toolbar_order()]


# ── Auto-loader ──────────────────────────────────────────────────────────

def load_gates():
    """Import every .py file in the gates/ directory.

    Each file is expected to call register() at module scope.
    Files are loaded in sorted order so that `order` values are predictable.
    """
    gates_dir = os.path.join(os.path.dirname(__file__), "gates")
    if not os.path.isdir(gates_dir):
        return
    for fname in sorted(os.listdir(gates_dir)):
        if fname.endswith(".py") and not fname.startswith("__"):
            mod_name = f"gates.{fname[:-3]}"
            importlib.import_module(mod_name)
