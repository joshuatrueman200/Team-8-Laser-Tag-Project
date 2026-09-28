import pygame
from view import View
from model import Model
from controller import Controller
import argparse as arg

# Arguments (create them in such a format)
parser = arg.ArgumentParser()
parser.add_argument("--music_off", action="store_true", help="Activate it to shut music off")

args = parser.parse_args()

# Store argument result in a variable
music_off = args.music_off

pygame.init()

# Window setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Laser Tag")

model = Model()
view = View(screen, model)
controller = Controller(model, view)

# Music running
if not music_off:
    pygame.mixer.music.load("Asset/photon_tracks_Track01.mp3")
    pygame.mixer.music.set_volume(1) # 0 Min/1 Max
    pygame.mixer.music.play(-1, start= 180) # Skips first 3 minutes to get to the goo stuff


# Main loop to keep the window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            controller.handle_event(event)

    controller.update()
    pygame.display.update()


controller.close()
pygame.quit()
