import pygame
import time

#########################################################################
# It displays the logo for 3 seconds before going into player ent scr
def splash_screen(screen):
    # Load logo
    logo = pygame.image.load("Asset/logo.jpg")
    logo = pygame.transform.scale(logo, (500, 300))

    # Display logo for 3 seconds
    screen.fill((0, 0, 0))
    screen.blit(logo, (150, 150))
    pygame.display.update()
    time.sleep(3)

#######################################################################
# Allows the operator to enter a player ID
# retrieve the player's code name from the database
# add a new code name if the player ID is not found
def player_entry_screen(screen):

    # Clear the splash screen
    screen.fill((0, 0, 0))

    # INSERT PLAYER ENTRY SCREEN CODE HERE||
    # Replace the placeholder code below  \/ with the player entry screen.
    #######################################################################
    font = pygame.font.Font(None, 35)
    text = font.render("INSERT PLAYER ENTRY SCREEN CODE HERE, GOOD LUCK", True, (255, 255, 255))
    text_rect = text.get_rect(center=(400, 300))
    screen.blit(text, text_rect)
    #######################################################################

    pygame.display.update()