import pygame

class Controller():

    # Constructor
    def __init__(self, model, view):
        self.model = model
        self.view = view

    # Looks for the first row with no data
    def first_incomplete_row(self, rows):
        for i, data in enumerate(rows):
            if not data["id"] or not data["codename"]:
                return i
        return len(rows) - 1
    
    #Keyboard inputs
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        ########################################################
        # PLAYER ENTRY SCREEN EVENTS
        if self.view.player_entry_screen:
            # Display Game Screen with F5
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                if self.view.player_entry_screen:
                    self.view.player_entry_screen = False
                    self.view.game_screen = True

            # Select which team you want to write on with "."
            if event.unicode == ".":
                self.view.current_team = "green" if self.view.current_team == "red" else "red"
                new_rows = self.view.red_rows if self.view.current_team == "red" else self.view.green_rows
                self.view.row = self.first_incomplete_row(new_rows)
                self.view.col = 0
                return



            rows = self.view.red_rows if self.view.current_team == "red" else self.view.green_rows
            current = rows[self.view.row]

            # Type ID
            if self.view.col == 0:
                if event.key == pygame.K_RETURN:
                    if current["id"]:
                        self.view.col = 1
                elif event.key == pygame.K_BACKSPACE:
                    current["id"] = current["id"][:-1]
                elif event.unicode.isdigit():
                    current["id"] += event.unicode

            # Type Code Name
            else: 
                if event.key == pygame.K_RETURN:
                    if current["codename"]:
                        if self.view.row < 14:
                            self.view.row += 1
                        self.view.col = 0
                elif event.key == pygame.K_BACKSPACE:
                    current["codename"] = current["codename"][:-1]
                elif event.unicode.isprintable():
                    current["codename"] += event.unicode

            

    def update(self):
        self.view.update()