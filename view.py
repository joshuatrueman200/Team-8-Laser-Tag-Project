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
        self.network_source = "127.0.0.1"
        self.network_destination = "127.0.0.1"
        self.network_field = 0
        self.status = ""
        self.hardware_popup = False

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
        self.draw_instructions()
        self.show_game_controls()

    def show_game_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("Game screen", True, (255, 255, 255))
        title_rect = title.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(title, title_rect)

    def show_network_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 32)
        lines = ["UDP Network (F9)",
                 f"Source IP: {self.network_source}" + (" <" if self.network_field == 0 else ""),
                 f"Destination/Broadcast IP: {self.network_destination}" + (" <" if self.network_field == 1 else ""),
                 "TAB: switch field   ENTER: save   ESC: cancel",
                 "Local test: 127.0.0.1 -> 127.0.0.1"]
        for i, line in enumerate(lines):
            self.screen.blit(font.render(line, True, (255, 255, 255)), (55, 100 + i * 65))
        self.draw_status()

    def draw_status(self):
        if self.status:
            font = pygame.font.Font(None, 22)
            self.screen.blit(font.render(self.status[:95], True, (255, 255, 0)), (80, 565))

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
        tiny = pygame.font.Font(None, 16)
        # Keep each heading aligned with its field and leave clear gaps between columns.
        id_x = x
        name_x = x + 70
        hardware_x = x + 195
        self.screen.blit(tiny.render("PLAYER ID", True, color), (id_x, 65))
        self.screen.blit(tiny.render("NAME", True, color), (name_x, 65))
        self.screen.blit(tiny.render("HW ID", True, color), (hardware_x, 65))

        row_height = 30
        for i, data in enumerate(rows):
            y = 80 + i * row_height
            id_box = pygame.Rect(id_x, y, 62, row_height - 4)
            codename_box = pygame.Rect(name_x, y, 118, row_height - 4)
            hardware_box = pygame.Rect(hardware_x, y, 82, row_height - 4)

            pygame.draw.rect(self.screen, color, id_box, 1)
            pygame.draw.rect(self.screen, color, codename_box, 1)
            pygame.draw.rect(self.screen, color, hardware_box, 1)

            # Draw player text only when this spot has a value.
            # Clip displayed values to their own column so long IDs/names never
            # spill into and visually collide with the next field.
            for key, box in (("id", id_box), ("codename", codename_box),
                             ("hardware_id", hardware_box)):
                value = str(data.get(key, "") or "")
                if value:
                    available_width = box.width - 6
                    shown = value
                    while shown and font.size(shown)[0] > available_width:
                        shown = shown[:-1]
                    if shown != value and len(shown) > 1:
                        shown = shown[:-1] + "…"
                    value_surface = font.render(shown, True, (255, 255, 255))
                    self.screen.blit(value_surface, (box.x + 3, box.y + 5))

            # Mark the cell that will get the next key press.
            if is_active and i == self.row:
                highlight_box = (id_box, codename_box, hardware_box)[self.col]
                pygame.draw.rect(self.screen, (255, 255, 0), highlight_box.inflate(4, 4), 2)

    def draw_instructions(self):
        # Keep instructions inside the narrow gap between the two team panels.
        # Wrap each instruction so it never overlaps the player input columns.
        font = pygame.font.Font(None, 16)
        max_width = 112
        fields = [
            ["Write your Player ID", "ENTER: look up name", "TAB: next field"],
            ["Write your Codename", "ENTER: hardware ID", "TAB: next field"],
            ["Write Hardware ID", "ENTER: save player", "TAB: next field"],
        ]
        instructions = list(fields[self.col]) + ["Press '.' to switch team"]

        wrapped_lines = []
        for instruction in instructions:
            words = instruction.split()
            line = ""
            for word in words:
                candidate = word if not line else f"{line} {word}"
                if font.size(candidate)[0] <= max_width:
                    line = candidate
                else:
                    if line:
                        wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
            wrapped_lines.append("")
        if wrapped_lines and wrapped_lines[-1] == "":
            wrapped_lines.pop()

        # Center each instruction line in the actual gap between the panels:
        # the left hardware column ends at x=327 and the right panel begins at x=450.
        left_edge_of_gap = 327
        right_edge_of_gap = 450
        x_center = (left_edge_of_gap + right_edge_of_gap) // 2
        y = 190
        line_height = 17
        for line in wrapped_lines:
            if line:
                text = font.render(line, True, (255, 255, 255))
                text_rect = text.get_rect(midtop=(x_center - text.get_width() // 2, y))
                # Explicitly center the rendered line horizontally on the gap.
                text_rect.centerx = x_center
                self.screen.blit(text, text_rect)
            y += line_height



    # Show the keyboard controls along the bottom.
    def show_game_controls(self):
        controls =(
            (10, ("F5", "Start", "Game")),
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