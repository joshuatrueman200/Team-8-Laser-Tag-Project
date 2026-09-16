import pygame
from view import splash_screen, player_entry_screen
pygame.init()

# Window setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Laser Tag")

# Music(true) or no music(false)
music = True
if music:
    pygame.mixer.music.load("Asset/photon_tracks_Track01.mp3")
    pygame.mixer.music.set_volume(1) # 0 Min/1 Max
    pygame.mixer.music.play(-1, start= 180) # Skips first 3 minutes to get to the goo stuff


# Calls the splash screen for 3 secs
# Then transitions to the player entry screen
splash_screen(screen)
player_entry_screen(screen)


# Main loop to keep the window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
