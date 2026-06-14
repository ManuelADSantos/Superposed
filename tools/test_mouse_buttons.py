from __future__ import annotations

import pygame


BUTTON_NAMES = {
    1: "left",
    2: "middle",
    3: "right",
    4: "scroll up",
    5: "scroll down",
}


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Mouse Button Tester")
    pygame.display.set_mode((320, 180))

    print("Press mouse buttons in the window. Close the window or press Esc to quit.")
    print("The script prints every mouse button event and its raw button number.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button_name = BUTTON_NAMES.get(event.button, "unknown")
                print(f"Mouse button pressed: {event.button} ({button_name})", flush=True)
            elif event.type == pygame.MOUSEBUTTONUP:
                button_name = BUTTON_NAMES.get(event.button, "unknown")
                print(f"Mouse button released: {event.button} ({button_name})", flush=True)
            elif event.type == pygame.MOUSEWHEEL:
                print(f"Mouse wheel: x={event.x} y={event.y} precise={getattr(event, 'precise_x', None)},{getattr(event, 'precise_y', None)}", flush=True)
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                key_name = pygame.key.name(event.key)
                print(f"Keyboard event: {pygame.event.event_name(event.type)} key={event.key} ({key_name})", flush=True)
            else:
                print(f"Event: {pygame.event.event_name(event.type)} {event.dict}", flush=True)

    pygame.quit()


if __name__ == "__main__":
    main()