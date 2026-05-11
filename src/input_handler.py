"""Input handling: keyboard and mouse."""

import pygame

from config import TILE_SIZE
from entities import BuildingType, Direction
from world import screen_to_world, get_tile, in_bounds


def rotate_direction(direction):
    """Rotate a direction 90 degrees clockwise."""
    return Direction((direction.value + 1) % 4)


def handle_input(dt, selected_building, selected_rotation, paused, step_requested):
    """Process input events and update game state."""
    import world as world_module
    
    keys = pygame.key.get_pressed()

    speed = 600 * dt

    if keys[pygame.K_w]:
        world_module.camera_y -= speed
    if keys[pygame.K_s]:
        world_module.camera_y += speed
    if keys[pygame.K_a]:
        world_module.camera_x -= speed
    if keys[pygame.K_d]:
        world_module.camera_x += speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, selected_building, selected_rotation, paused, step_requested

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False, selected_building, selected_rotation, paused, step_requested

            if event.key == pygame.K_1:
                selected_building = BuildingType.BELT

            elif event.key == pygame.K_2:
                selected_building = BuildingType.GENERATOR

            elif event.key == pygame.K_3:
                selected_building = BuildingType.HADAMARD

            elif event.key == pygame.K_4:
                selected_building = BuildingType.X_GATE

            elif event.key == pygame.K_5:
                selected_building = BuildingType.MEASUREMENT

            elif event.key == pygame.K_r:
                selected_rotation = rotate_direction(selected_rotation)

            elif event.key == pygame.K_p:
                paused = not paused

            elif event.key == pygame.K_n and paused:
                step_requested = True

        if event.type == pygame.MOUSEWHEEL:
            world_module.zoom += event.y * 0.1
            world_module.zoom = max(0.4, min(2.5, world_module.zoom))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            wx, wy = screen_to_world(mx, my, TILE_SIZE)

            if in_bounds(wx, wy):
                tile = get_tile(wx, wy)

                if event.button == 1:
                    tile.building = selected_building
                    tile.direction = selected_rotation

                elif event.button == 3:
                    tile.building = BuildingType.EMPTY
                    tile.item = None

    return True, selected_building, selected_rotation, paused, step_requested
