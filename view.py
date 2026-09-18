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
        self.game_screen = False

    #########################################################################
    # It displays the logo for 3 seconds before going into player ent scr
    def show_splash_screen(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (150,150))
        pygame.display.update()
        time.sleep(3)

    def show_player_entry_screen(self):
        self.screen.fill((0, 0, 0))
        self._draw_panel(50, (255, 0, 0), "RED TEAM")
        self._draw_panel(450, (0, 205, 0), "GREEN TEAM")
        self.show_game_controls()

    def show_game_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("Game screen", True, (255, 255, 255))
        title_rect = title.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(title, title_rect)

    def update(self):

        # show splash screen
        if self.splash_screen:
            self.show_splash_screen()
            self.splash_screen = False
            self.player_entry_screen = True

        # show player entry screen
        elif self.player_entry_screen:
            self.show_player_entry_screen()

        # show game screen
        elif self.game_screen:
            self.show_game_screen()

    def _draw_panel(self, x, color, label):
        font = pygame.font.Font(None, 24)
        title = font.render(label, True, color)
        self.screen.blit(title, (x, 40))

    #CONTROLS PANEL HERE
    # F5 starts the game
    # F12 clears the game.
    def show_game_controls(self):
        controls =(
            (10, ("F5", "Start", "Game")),
            (self.screen.get_width() - 60, ("F12", "Clear", "Game")),
        )

        #Draws the controls on the screen
        for x, lines in controls:
            self.draw_control(x, lines)

    # box and font for the controls
    def draw_control(self, x, lines): 
        #White outline for boxes
        control = pygame.Rect(x, self.screen.get_height() - 60, 50, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), control, 1)

        # Draw the text inside the box
        font = pygame.font.Font(None, 14)
        for index, line in enumerate(lines):
            title = font.render(line, True, (255, 255, 255)) #White but we can changre it to green
            title_rect = title.get_rect(center=(control.centerx, control.y + 10 + index * 14))
            self.screen.blit(title, title_rect)