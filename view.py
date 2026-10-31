import time
import pygame

class View:
    # Draw the game screens and team lists.

    def __init__(self, screen, model):

        self.screen = screen
        self.model = model
        self.current_team = "red"
        self.row = 0
        self.col = 0

        # Load the game logo.
        self.logo = pygame.image.load("Asset/logo.jpg")
        self.logo = pygame.transform.scale(self.logo, (500, 300))

        # Remember which screen to draw.
        self.splash_screen = True
        self.player_entry_screen = False
        self.game_screen = False
        self.network_screen = False
        self.network_destination = "127.0.0.1"
        self.status = ""
        self.hardware_popup = False
        self.game_timer_label = ""
        self.game_final_score = None
        self.game_in_progress = False

    # Show the logo before the player list.
    def show_splash_screen(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.logo, (150,150))
        pygame.display.update()
        time.sleep(3)

    # Show both team lists and their controls.
    def show_player_entry_screen(self):
        self.screen.fill((0, 0, 0))
        self.draw_panel(50, (255, 0, 0), "RED TEAM", self.model.red_rows, self.current_team == "red")
        self.draw_panel(450, (0, 205, 0), "GREEN TEAM", self.model.green_rows, self.current_team == "green")
        self.draw_game_timer()
        self.draw_instructions()
        self.show_game_controls()
        if self.hardware_popup:
            self.draw_hardware_popup()

    def show_game_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("Game screen", True, (255, 255, 255))
        title_rect = title.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(title, title_rect)

    def show_network_screen(self):
        self.screen.fill((0, 0, 0))
        self.draw_game_timer()
        font = pygame.font.Font(None, 24)
        lines = ["UDP Network (F9)",
                 "Receive on: 0.0.0.0:7501 (all IPv4 addresses)",
                 f"Transmit to IP: {self.network_destination} <",
                 "ENTER: save  ESC: cancel",
                 "Local test: 127.0.0.1   LAN broadcast: e.g. 192.168.1.255"]
        for i, line in enumerate(lines):
            self.screen.blit(font.render(line, True, (255, 255, 255)), (55, 100 + i * 65))
        self.draw_status()

    def draw_status(self):
        if self.status:
            font = pygame.font.Font(None, 22)
            self.screen.blit(font.render(self.status[:95], True, (255, 255, 0)), (80, 565))

    def draw_game_timer(self):
        if self.game_final_score is not None:
            red_score, green_score = self.game_final_score
            if red_score == green_score:
                message = f"GAME OVER - TIE {red_score} : {green_score}"
            else:
                winner = "RED" if red_score > green_score else "GREEN"
                message = f"GAME OVER - {winner} WINS {red_score} : {green_score}"
            color = (255, 220, 100)
        elif self.game_timer_label:
            message = self.game_timer_label
            color = (255, 255, 255)
        else:
            return

        font = pygame.font.Font(None, 26)
        rendered = font.render(message, True, color)
        self.screen.blit(rendered, rendered.get_rect(center=(400, 18)))

    def draw_hardware_popup(self):
        box = pygame.Rect(0, 0, 360, 130)
        box.center = self.screen.get_rect().center
        pygame.draw.rect(self.screen, (30, 30, 30), box)
        pygame.draw.rect(self.screen, (255, 255, 0), box, 2)

        font = pygame.font.Font(None, 26)
        small = pygame.font.Font(None, 20)

        title = font.render("Enter Hardware ID", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(box.centerx, box.y + 28)))

        rows = self.model.red_rows if self.current_team == "red" else self.model.green_rows
        field = pygame.Rect(box.x + 90, box.y + 50, 180, 32)
        pygame.draw.rect(self.screen, (255, 255, 255), field, 1)
        number = font.render(rows[self.row]["hardware_id"], True, (255, 255, 255))
        self.screen.blit(number, (field.x + 6, field.y + 7))

        hint = small.render("ENTER: confirm   ESC: cancel", True, (200, 200, 200))
        self.screen.blit(hint, hint.get_rect(center=(box.centerx, box.y + 108)))

    def update(self):
        if self.splash_screen:
            self.show_splash_screen()
            self.splash_screen = False
            self.player_entry_screen = True
        elif self.network_screen:
            self.show_network_screen()
        elif self.player_entry_screen:
            self.show_player_entry_screen()
            self.draw_status()
        elif self.game_screen:
            self.show_game_screen()


    # Draw one team's player rows.
    def draw_panel(self, x, color, label, rows, is_active):
        # Title of the panel
        font = pygame.font.Font(None, 24)
        title = font.render(label, True, color)
        self.screen.blit(title, (x, 40))


        row_height = 30
        for i, data in enumerate(rows):
            y = 80 + i * row_height
            id_box = pygame.Rect(x, y, 40, row_height - 4)
            codename_box = pygame.Rect(x + 45, y, 150, row_height - 4)

            pygame.draw.rect(self.screen, color, id_box, 1)

            pygame.draw.rect(self.screen, color, codename_box, 1)

            # Draw player text only when this spot has a value.
            if data["id"]:
                id_text = font.render(data["id"], True, (255, 255, 255))
                self.screen.blit(id_text, (id_box.x + 3, id_box.y + 5))
            if data["codename"]:
                codename_text = font.render(data["codename"], True, (255, 255, 255))
                self.screen.blit(codename_text, (codename_box.x + 3, codename_box.y + 5))

            # Mark the cell that will get the next key press.
            if is_active and i == self.row:
                highlight_box = id_box if self.col == 0 else codename_box
                pygame.draw.rect(self.screen, (255, 255, 0), highlight_box.inflate(4, 4), 2)

    def draw_instructions(self):
        font = pygame.font.Font(None, 20)

        if self.col == 0:
            lines = [
                "Write your Player ID",
                "TAB or ENTER moves to",
                "the codename field."
            ]
        else:
            lines = [
                "Write your Codename",
                "TAB returns to the ID.",
                "ENTER saves the player."
            ]

        lines += ["", "Press '.' to", "switch team"]

        x_center = 342
        y = 200

        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x_center, y))
            self.screen.blit(text, text_rect)
            y += 25



    # Show the keyboard controls along the bottom.
    def show_game_controls(self):
        play_action_control = (
            ("F5", "View", "Game")
            if self.game_in_progress
            else ("F5", "Start", "Game")
        )
        controls =(
            (10, play_action_control),
            (self.screen.get_width() - 185, ("DEL", "Delete", "Player")),
            (self.screen.get_width() - 125, ("F9", "UDP", "Network")),
            (self.screen.get_width() - 60, ("F12", "Clear", "Game")),
        )

        for x, lines in controls:
            self.draw_control(x, lines)

    # Draw one small control box.
    def draw_control(self, x, lines): 
        control = pygame.Rect(x, self.screen.get_height() - 60, 50, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), control, 1)

        font = pygame.font.Font(None, 14)
        for index, line in enumerate(lines):
            title = font.render(line, True, (255, 255, 255))
            title_rect = title.get_rect(center=(control.centerx, control.y + 10 + index * 14))
            self.screen.blit(title, title_rect)