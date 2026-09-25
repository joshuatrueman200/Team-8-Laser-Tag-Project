import pygame
from database import PlayerDatabaseError
from udp_manager import UDPManager

class Controller():

    # Constructor
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.udp = UDPManager()
        self.added_rows = set()
        self.network_field = 0
        self.network_source = self.udp.source_ip
        self.network_destination = self.udp.destination_ip
        self.status = ""

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
        if self.view.network_screen:
            if event.key == pygame.K_ESCAPE:
                self.view.network_screen = False
                return
            if event.key == pygame.K_TAB:
                self.network_field = 1 - self.network_field
                return
            if event.key == pygame.K_RETURN:
                try:
                    self.udp.change_network(self.network_source, self.network_destination)
                except (ValueError, OSError) as error:
                    self.status = f"Network error: {error}"
                else:
                    self.status = f"UDP: {self.udp.source_ip} -> {self.udp.destination_ip}:7500"
                    self.view.network_screen = False
                return
            value = self.network_source if self.network_field == 0 else self.network_destination
            if event.key == pygame.K_BACKSPACE:
                value = value[:-1]
            elif event.unicode in "0123456789.":
                value += event.unicode
            if self.network_field == 0:
                self.network_source = value
            else:
                self.network_destination = value
            return


        if self.view.player_entry_screen:
            if event.key == pygame.K_F9:
                self.network_source = self.udp.source_ip
                self.network_destination = self.udp.destination_ip
                self.network_field = 0
                self.view.network_screen = True
                return
            # Display Game Screen with F5
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                    self.view.player_entry_screen = False
                    self.view.game_screen = True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                self.model.clear_teams()
                self.added_rows.clear()
                self.view.row = 0
                self.view.col = 0
                self.status = "Roster cleared from screen only; database unchanged"

            if event.key == pygame.K_TAB:
                self.view.col = 1 - self.view.col
                return

            

            # Select which team you want to write on with "."
            if event.unicode == ".":
                self.view.current_team = "green" if self.view.current_team == "red" else "red"
                new_rows = self.model.red_rows if self.view.current_team == "red" else self.model.green_rows
                self.view.row = self.first_incomplete_row(new_rows)
                current = new_rows[self.view.row]
                self.view.col = 0 if not current["id"] else 1
                return



            rows = self.model.red_rows if self.view.current_team == "red" else self.model.green_rows
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
                    if current["id"] and current["codename"]:
                        key = (self.view.current_team, self.view.row)
                        if key not in self.added_rows:
                            try:
                                self.model.add_player(current["id"], current["codename"])
                            except PlayerDatabaseError as error:
                                self.status = f"Database save failed: {error}"
                                return
                            self.added_rows.add(key)
                            self.status = f"Saved player {current['id']} ({current['codename']}) to database"
                            try:
                                self.udp.broadcast_equipment_code(current["id"])
                            except OSError as error:
                                self.status += f"; UDP send failed: {error}"
                            else:
                                self.status += f"; sent to {self.udp.destination_ip}:7500"
                        if self.view.row < 14:
                            self.view.row += 1
                        self.view.col = 0
                elif event.key == pygame.K_BACKSPACE:
                    current["codename"] = current["codename"][:-1]
                elif event.unicode.isprintable():
                    current["codename"] += event.unicode

            

    def update(self):
        for data, address in self.udp.receive_messages():
            print(f"UDP received from {address}: {data!r}")
        self.view.network_source = self.network_source
        self.view.network_destination = self.network_destination
        self.view.network_field = self.network_field
        self.view.status = self.status
        self.view.update()

    def close(self):
        self.udp.close()
