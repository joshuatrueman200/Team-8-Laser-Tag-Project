import pygame
import time

class View():

    # Constructor 
    def __init__(self, screen):
        self.screen = screen

        # Load logo
        self.logo = pygame.image.load("Asset/logo.jpg")
        self.logo = pygame.transform.scale(self.logo, (500, 300))

        # Screens
        self.splash_screen = True
        self.player_entry_screen = False

    #########################################################################
    # It displays the logo for 3 seconds before going into player ent scr
    def show_splash_screen(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (150,150))
        pygame.display.update()
        time.sleep(3)

    def update(self):

        # show splash screen
        if self.splash_screen:
            self.show_splash_screen()
            self.splash_screen = False
            self.player_entry_screen = True

        # show player entry screen
        elif self.player_entry_screen:
            self.screen.fill((0, 0, 0))
            self._draw_panel(50, (255, 0, 0), "RED TEAM")
            self._draw_panel(450, (0, 205, 0), "GREEN TEAM")
        

    def _draw_panel(self, x, color, label):
        font = pygame.font.Font(None, 24)
        title = font.render(label, True, color)
        self.screen.blit(title, (x, 40))