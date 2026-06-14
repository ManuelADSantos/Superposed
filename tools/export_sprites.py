#!/usr/bin/env python3
"""Export all gate sprites as 64x64 PNGs to assets/gates_sprites/."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

from src.engine.gate_registry import load_gates, GATES
from src.core.entities import Direction
from src.ui.sprites import get_building_sprite

load_gates()

out = os.path.join(os.path.dirname(__file__), "..", "assets", "gates_sprites")
os.makedirs(out, exist_ok=True)

for gid, gate in sorted(GATES.items()):
    sprite = get_building_sprite(gid, Direction.RIGHT, 64)
    if sprite is None:
        continue
    path = os.path.join(out, f"{gid}.png")
    pygame.image.save(sprite, path)
    print(f"  {gid}.png")

pygame.quit()
print(f"Done — {len(os.listdir(out))} sprites in assets/gates_sprites/")
