import pygame
from controller import Controller
from database import PlayerDatabase
from model import Model
from view import View
import argparse as arg


def main():
    # Start Pygame and build the game parts.
    pygame.init()
    controller = None

    parser = arg.ArgumentParser()

    # Purely for testing purposes
    parser.add_argument("--music_off", action="store_true", help = "Place to shut off music ingame")
    args = parser.parse_args()

    music_off = args.music_off

    try:
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Laser Tag")

        model = Model(PlayerDatabase())
        view = View(screen, model)
        controller = Controller(model, view, music_off)

        # Keep the window open until the player closes it.
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWCLOSE:
                    if controller.is_action_window_event(event):
                        controller.stop_play_action()
                    else:
                        running = False
                else:
                    controller.handle_event(event)

            controller.update()
            pygame.display.update()
            clock.tick(30)
    finally:
        # Close the UDP sockets and Pygame even if the game hits an error.
        if controller is not None:
            controller.close()
        pygame.quit()


if __name__ == "__main__":
    main()
