import pygame
import time

class View():

    # Constructor 
    def __init__(self, screen):
        self.screen = screen

        # Load logo
        self.logo = pygame.image.load("Asset/logo.jpg")
        self.logo = pygame.transform.scale(self.logo, (500, 300))

    #########################################################################
    # It displays the logo for 3 seconds before going into player ent scr
    def splash_screen(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (150,150))
        pygame.display.update()
        time.sleep(3)

    #######################################################################
    # Allows the operator to enter a player ID
    # retrieve the player's code name from the database
    # add a new code name if the player ID is not found
    def player_entry_screen(self):
         # Clear the splash screen
            self.screen.fill((0, 0, 0))
        
            # INSERT PLAYER ENTRY SCREEN CODE HERE||
            # Replace the placeholder code below  \/ with the player entry screen.
            #######################################################################
            font = pygame.font.Font(None, 35)
            text = font.render("INSERT PLAYER ENTRY SCREEN CODE HERE, GOOD LUCK", True, (255, 255, 255))
            text_rect = text.get_rect(center=(400, 300))
            self.screen.blit(text, text_rect)
            #######################################################################
        
            pygame.display.update()