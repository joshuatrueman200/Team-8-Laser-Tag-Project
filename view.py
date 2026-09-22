import pygame
import time

class View():

    # Constructor 
    def __init__(self, screen, model):

        self.screen = screen
        self.model = model
        self.current_team = "red"
        self.row = 0
        self.col = 0

        # Load logo
        self.logo = pygame.image.load("Asset/logo.jpg")
        self.logo = pygame.transform.scale(self.logo, (500, 300))

        # Screens
        self.splash_screen = True
        self.player_entry_screen = False
        self.game_screen = False

    # GETTERS
    def get_current_team(self):
        return self.current_team

    #########################################################################
    # It displays the logo for 3 seconds before going into player ent scr
    def show_splash_screen(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (150,150))
        pygame.display.update()
        time.sleep(3)

    # Displays the player entry screen
    def show_player_entry_screen(self):
        self.screen.fill((0, 0, 0))
        self.draw_panel(50, (255, 0, 0), "RED TEAM", self.model.red_rows, self.current_team == "red")
        self.draw_panel(450, (0, 205, 0), "GREEN TEAM", self.model.green_rows, self.current_team == "green")
        self.draw_instructions()
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


    # Draws the panels to write user data
    def draw_panel(self, x, color, label, rows, is_active):
        # Title of the panel
        font = pygame.font.Font(None, 24)
        title = font.render(label, True, color)
        self.screen.blit(title, (x, 40))


        row_height = 30
        for i, data in enumerate(rows):
            y = 80 + i * row_height
            id_box = pygame.Rect(x, y, 30, row_height - 4)
            codename_box = pygame.Rect(x + 35, y, 150, row_height - 4)

            # Draw ID Box
            pygame.draw.rect(self.screen, color, id_box, 1)

            # Draw Codename Box
            pygame.draw.rect(self.screen, color, codename_box, 1)

            # Checks if there is data to write
            if data["id"]:
                id_text = font.render(data["id"], True, (255, 255, 255))
                self.screen.blit(id_text, (id_box.x + 3, id_box.y + 5))
            if data["codename"]:
                codename_text = font.render(data["codename"], True, (255, 255, 255))
                self.screen.blit(codename_text, (codename_box.x + 3, codename_box.y + 5))

            # Highlights the current cell you are wring on
            if is_active and i == self.row:
                highlight_box = id_box if self.col == 0 else codename_box
                pygame.draw.rect(self.screen, (255, 255, 0), highlight_box.inflate(4, 4), 2)

    def draw_instructions(self):
        font = pygame.font.Font(None, 20)

        if self.col == 0:
            lines = [
                "Write your Player ID",
                "and press ENTER to confirm."
            ]
        else:
            lines = [
                "Write your Codename",
                "and press ENTER to confirm."
            ]

        lines += ["", "Press '.' to", "switch team"]

        x_center = 342
        y = 200

        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x_center, y))
            self.screen.blit(text, text_rect)
            y += 25



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