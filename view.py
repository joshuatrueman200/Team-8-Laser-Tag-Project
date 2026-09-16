import pygame
import time

def splash_screen():
    pygame.init()

    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Laser Tag")

    # Load logo
    logo = pygame.image.load("Assets/logo.jpg")

    # Resize logo
    logo = pygame.transform.scale(logo, (500, 300))

    # Display logo
    screen.fill((0, 0, 0))
    screen.blit(logo, (150, 150))
    pygame.display.update()

    # Keep splash screen for 3 seconds
    time.sleep(3)

    pygame.quit()


splash_screen()
