import random
from typing import Optional

import pygame
from enum import Enum

# ============================================================
# Minimal Shapez-style Factory Game in Pygame
# ------------------------------------------------------------
# Features:
# - Grid world
# - Conveyor belts
# - Shape generators
# - Shape movement
# - Basic camera movement
# - Build mode
#
# Controls:
# WASD            -> Move camera
# Mouse Wheel     -> Zoom
# 1               -> Conveyor
# 2               -> Generator
# 3               -> Trash
# R               -> Rotate selected building
# Left Click      -> Place building
# Right Click     -> Remove building
# ESC             -> Quit
#
# Requirements:
# pip install pygame
# ============================================================

pygame.init()

WIDTH = 1280
HEIGHT = 720
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Superposed - Quantum Factory Prototype")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 18)

TILE_SIZE = 64
WORLD_W = 100
WORLD_H = 100

BG = (20, 20, 25)
GRID = (40, 40, 50)
WHITE = (230, 230, 230)
YELLOW = (255, 220, 90)
RED = (220, 80, 80)
GREEN = (100, 220, 120)
BLUE = (100, 160, 255)
ORANGE = (255, 160, 80)


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


DIR_VECTORS = {
    Direction.UP: (0, -1),
    Direction.RIGHT: (1, 0),
    Direction.DOWN: (0, 1),
    Direction.LEFT: (-1, 0),
}


class BuildingType(Enum):
    EMPTY = 0
    BELT = 1
    GENERATOR = 2
    HADAMARD = 3
    X_GATE = 4
    MEASUREMENT = 5


class QubitState(Enum):
    ZERO = 0
    ONE = 1
    SUPERPOSITION = 2


def state_color(state):
    if state == QubitState.ZERO:
        return RED
    if state == QubitState.ONE:
        return BLUE
    return ORANGE


class QubitItem:
    def __init__(self, state=QubitState.ZERO):
        self.progress = 0.0
        self.state = state

    def draw(self, surface, x, y, size):
        cx = x + size // 2
        cy = y + size // 2

        if self.state == QubitState.SUPERPOSITION:
            pygame.draw.circle(surface, ORANGE, (cx, cy), size // 4)
            pygame.draw.circle(surface, WHITE, (cx, cy), size // 4, 2)
        else:
            pygame.draw.circle(surface, state_color(self.state), (cx, cy), size // 5)


class Tile:
    def __init__(self):
        self.building = BuildingType.EMPTY
        self.direction = Direction.RIGHT
        self.item: Optional[QubitItem] = None
        self.spawn_timer = 0
        self.measurements = []
        self.measure_flash = 0.0


world = [[Tile() for _ in range(WORLD_H)] for _ in range(WORLD_W)]


camera_x = 0
camera_y = 0
zoom = 1.0

selected_building = BuildingType.BELT
selected_rotation = Direction.RIGHT
paused = False
step_requested = False


BELT_SPEED = 1.8
GENERATOR_SPEED = 2.0


def world_to_screen(wx, wy):
    size = TILE_SIZE * zoom
    sx = (wx * size) - camera_x
    sy = (wy * size) - camera_y
    return sx, sy



def screen_to_world(sx, sy):
    size = TILE_SIZE * zoom
    wx = int((sx + camera_x) // size)
    wy = int((sy + camera_y) // size)
    return wx, wy



def in_bounds(x, y):
    return 0 <= x < WORLD_W and 0 <= y < WORLD_H



def rotate_direction(direction):
    return Direction((direction.value + 1) % 4)


def transform_qubit(building, item):
    if building == BuildingType.HADAMARD:
        if item.state in (QubitState.ZERO, QubitState.ONE):
            item.state = QubitState.SUPERPOSITION
        else:
            item.state = random.choice([QubitState.ZERO, QubitState.ONE])
    elif building == BuildingType.X_GATE:
        if item.state == QubitState.ZERO:
            item.state = QubitState.ONE
        elif item.state == QubitState.ONE:
            item.state = QubitState.ZERO
    elif building == BuildingType.MEASUREMENT:
        if item.state == QubitState.SUPERPOSITION:
            item.state = random.choice([QubitState.ZERO, QubitState.ONE])
        return item.state


def record_measurement(tile, outcome):
    tile.measurements.append(outcome)
    if len(tile.measurements) > 12:
        tile.measurements.pop(0)
    tile.measure_flash = 0.35



def draw_arrow(surface, rect, direction, color=WHITE):
    cx = rect.centerx
    cy = rect.centery

    if direction == Direction.UP:
        points = [(cx, cy - 12), (cx - 10, cy + 8), (cx + 10, cy + 8)]
    elif direction == Direction.RIGHT:
        points = [(cx + 12, cy), (cx - 8, cy - 10), (cx - 8, cy + 10)]
    elif direction == Direction.DOWN:
        points = [(cx, cy + 12), (cx - 10, cy - 8), (cx + 10, cy - 8)]
    else:
        points = [(cx - 12, cy), (cx + 8, cy - 10), (cx + 8, cy + 10)]

    pygame.draw.polygon(surface, color, points)


def draw_building_label(surface, rect, label, color=WHITE):
    text = FONT.render(label, True, color)
    text_rect = text.get_rect(center=rect.center)
    surface.blit(text, text_rect)


def draw_measurement_histogram(surface, rect, tile):
    if tile.measurements:
        chart_rect = rect.inflate(-14, -22)
        chart_rect.height = max(16, chart_rect.height // 2)
        chart_rect.top = rect.top + 6

        zero_count = sum(1 for outcome in tile.measurements if outcome == QubitState.ZERO)
        one_count = sum(1 for outcome in tile.measurements if outcome == QubitState.ONE)
        total = max(1, zero_count + one_count)

        gap = 4
        bar_width = max(4, (chart_rect.width - gap) // 2)
        max_height = chart_rect.height - 4

        red_height = max(4, int(max_height * (zero_count / total)))
        blue_height = max(4, int(max_height * (one_count / total)))

        red_rect = pygame.Rect(chart_rect.left, chart_rect.bottom - red_height, bar_width, red_height)
        blue_rect = pygame.Rect(chart_rect.left + bar_width + gap, chart_rect.bottom - blue_height, bar_width, blue_height)

        pygame.draw.rect(surface, RED, red_rect)
        pygame.draw.rect(surface, BLUE, blue_rect)
        pygame.draw.rect(surface, WHITE, chart_rect, 1)

        timeline_y = chart_rect.bottom + 2
        timeline_width = chart_rect.width
        tick_width = max(2, timeline_width // 12)
        start_x = chart_rect.left

        for index, outcome in enumerate(tile.measurements[-12:]):
            tick_rect = pygame.Rect(start_x + index * tick_width, timeline_y, tick_width - 1, 4)
            pygame.draw.rect(surface, state_color(outcome), tick_rect)

    if tile.measure_flash > 0:
        alpha = int(180 * min(tile.measure_flash / 0.35, 1.0))
        flash_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(flash_surface, (255, 255, 255, alpha), flash_surface.get_rect(), 4, border_radius=6)
        surface.blit(flash_surface, rect.topleft)



def draw_grid():
    size = TILE_SIZE * zoom

    start_x = int(camera_x // size)
    end_x = int((camera_x + WIDTH) // size) + 2

    start_y = int(camera_y // size)
    end_y = int((camera_y + HEIGHT) // size) + 2

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            if not in_bounds(x, y):
                continue

            sx, sy = world_to_screen(x, y)
            rect = pygame.Rect(sx, sy, size, size)

            pygame.draw.rect(SCREEN, GRID, rect, 1)

            tile = world[x][y]

            if tile.building == BuildingType.BELT:
                pygame.draw.rect(SCREEN, BLUE, rect.inflate(-10, -10), border_radius=6)
                draw_arrow(SCREEN, rect, tile.direction)

            elif tile.building == BuildingType.GENERATOR:
                pygame.draw.rect(SCREEN, GREEN, rect.inflate(-10, -10), border_radius=6)
                draw_arrow(SCREEN, rect, tile.direction)
                draw_building_label(SCREEN, rect, "S")

            elif tile.building == BuildingType.HADAMARD:
                pygame.draw.rect(SCREEN, (170, 90, 255), rect.inflate(-10, -10), border_radius=6)
                draw_arrow(SCREEN, rect, tile.direction)
                draw_building_label(SCREEN, rect, "H")

            elif tile.building == BuildingType.X_GATE:
                pygame.draw.rect(SCREEN, (80, 220, 220), rect.inflate(-10, -10), border_radius=6)
                draw_arrow(SCREEN, rect, tile.direction)
                draw_building_label(SCREEN, rect, "X")

            elif tile.building == BuildingType.MEASUREMENT:
                pygame.draw.rect(SCREEN, (235, 190, 80), rect.inflate(-10, -10), border_radius=6)
                draw_arrow(SCREEN, rect, tile.direction)
                draw_building_label(SCREEN, rect, "M")
                draw_measurement_histogram(SCREEN, rect, tile)

            if tile.item:
                dx, dy = DIR_VECTORS[tile.direction]

                px = sx + size / 2 + (dx * tile.item.progress * size * 0.5)
                py = sy + size / 2 + (dy * tile.item.progress * size * 0.5)

                tile.item.draw(SCREEN, px - 10, py - 10, 20)



def update_items(dt):
    moved_items = []

    for y in range(WORLD_H):
        for x in range(WORLD_W):
            tile = world[x][y]

            if tile.measure_flash > 0:
                tile.measure_flash = max(0.0, tile.measure_flash - dt)

            if tile.building == BuildingType.GENERATOR:
                tile.spawn_timer += dt

                if tile.spawn_timer >= GENERATOR_SPEED:
                    tile.spawn_timer = 0

                    if tile.item is None:
                        tile.item = QubitItem(QubitState.ZERO)

            if tile.item:
                tile.item.progress += BELT_SPEED * dt

                if tile.item.progress >= 1.0:
                    moved_items.append((x, y))

    for x, y in moved_items:
        tile = world[x][y]

        if not tile.item:
            continue

        dx, dy = DIR_VECTORS[tile.direction]
        nx = x + dx
        ny = y + dy

        item = tile.item
        item.progress = 0

        if not in_bounds(nx, ny):
            tile.item = None
            continue

        next_tile = world[nx][ny]

        if next_tile.building in (
            BuildingType.HADAMARD,
            BuildingType.X_GATE,
            BuildingType.MEASUREMENT,
        ):
            outcome = transform_qubit(next_tile.building, item)

            if next_tile.building == BuildingType.MEASUREMENT:
                record_measurement(next_tile, outcome)
                tile.item = None
                continue

        if next_tile.building != BuildingType.EMPTY and next_tile.item is None:
            next_tile.item = item
            tile.item = None



def handle_input(dt):
    global camera_x
    global camera_y
    global zoom
    global selected_building
    global selected_rotation
    global paused
    global step_requested

    keys = pygame.key.get_pressed()

    speed = 600 * dt

    if keys[pygame.K_w]:
        camera_y -= speed
    if keys[pygame.K_s]:
        camera_y += speed
    if keys[pygame.K_a]:
        camera_x -= speed
    if keys[pygame.K_d]:
        camera_x += speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

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
            zoom += event.y * 0.1
            zoom = max(0.4, min(2.5, zoom))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            wx, wy = screen_to_world(mx, my)

            if in_bounds(wx, wy):
                tile = world[wx][wy]

                if event.button == 1:
                    tile.building = selected_building
                    tile.direction = selected_rotation

                elif event.button == 3:
                    tile.building = BuildingType.EMPTY
                    tile.item = None

    return True



def draw_ui():
    lines = [
        "1 = Belt",
        "2 = Generator",
        "3 = Hadamard",
        "4 = X Gate",
        "5 = Measure",
        "R = Rotate",
        "P = Pause",
        "N = Step (paused)",
        "WASD = Move Camera",
        "Mouse Wheel = Zoom",
    ]

    current = f"Selected: {selected_building.name} | Rotation: {selected_rotation.name}"
    status = "PAUSED" if paused else "RUNNING"

    y = 10

    for line in lines:
        text = FONT.render(line, True, WHITE)
        SCREEN.blit(text, (10, y))
        y += 22

    text = FONT.render(current, True, YELLOW)
    SCREEN.blit(text, (10, y + 10))

    status_text = FONT.render(status, True, GREEN if not paused else RED)
    SCREEN.blit(status_text, (10, y + 34))



def main():
    global step_requested

    running = True

    while running:
        dt = CLOCK.tick(FPS) / 1000.0

        running = handle_input(dt)

        if not paused or step_requested:
            update_items(dt)
            step_requested = False

        SCREEN.fill(BG)

        draw_grid()
        draw_ui()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
