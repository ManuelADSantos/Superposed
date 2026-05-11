"""Superposed: A Quantum Factory Puzzle Game.

Entry point and main game loop.
"""

import pygame

from config import WIDTH, HEIGHT, FPS, BG
from entities import BuildingType, Direction
from input_handler import handle_input
from simulation import update_items
from rendering import draw_grid, draw_ui


def main():
    """Main game loop."""
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Superposed")
    clock = pygame.time.Clock()

    # Game state
    selected_building = BuildingType.BELT
    selected_rotation = Direction.RIGHT
    paused = False
    step_requested = False

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        running, selected_building, selected_rotation, paused, step_requested = handle_input(
            dt, selected_building, selected_rotation, paused, step_requested
        )

        if not paused or step_requested:
            update_items(dt)
            step_requested = False

        screen.fill(BG)
        draw_grid(screen)
        draw_ui(screen, selected_building, selected_rotation, paused)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
