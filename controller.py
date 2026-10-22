import pygame
from database import PlayerDatabaseError
from udp_manager import UDPManager


class Controller:
    # Turn key presses into game, database, and network actions.

    MAX_PLAYER_ID_LENGTH = 4
    MAX_CODENAME_LENGTH = 15

    # Constructor
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.udp = UDPManager()
        self.added_rows = set()
        self._refresh_added_rows()
        self.network_field = 0
        self.network_source = self.udp.source_ip
        self.network_destination = self.udp.destination_ip
        self.status = ""
        self.pending_delete = None

    def _refresh_added_rows(self):
        # Track which filled spots are already saved.
        self.added_rows = {
            (team, index)
            for team, rows in (("red", self.model.red_rows), ("green", self.model.green_rows))
            for index, data in enumerate(rows)
            if data["id"] and data["codename"]
        }

    def current_team_rows(self):
        # Return the list for the team on screen.
        if self.view.current_team == "red":
            return self.model.red_rows
        return self.model.green_rows

    @classmethod
    def is_valid_codename(cls, codename):
        return (
            1 <= len(codename) <= cls.MAX_CODENAME_LENGTH
            and all(not character.isspace() for character in codename)
        )

    def current_player_needs_codename(self):
        current = self.current_team_rows()[self.view.row]
        return bool(current["id"]) and not self.is_valid_codename(current["codename"])

    def save_player(self, current):
        # Save the player; the hardware ID stays in the team row. Then go to the next row.
        self.view.hardware_popup = False

        previous_codename = self.model.database_players.get(current["id"])
        try:
            is_new_player = self.model.add_player(
                current["id"], current["codename"], self.view.current_team
            )
        except PlayerDatabaseError as error:
            self.status = f"Database save failed: {error}"
            return
        self._refresh_added_rows()

        team = self.view.current_team
        if is_new_player:
            self.status = f"Saved {current['id']} ({current['codename']}) to {team}"
        elif previous_codename != current["codename"]:
            self.status = f"Updated {current['id']} ({current['codename']}) in {team}"
        else:
            self.status = f"Assigned {current['id']} ({current['codename']}) to {team}"

        if self.view.row < 14:
            self.view.row += 1
        self.view.col = 0

    def first_incomplete_row(self, rows):
        # Find an open spot, or use the last spot if the team is full.
        for i, data in enumerate(rows):
            if not data["id"] or not data["codename"]:
                return i
        return len(rows) - 1

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Network screen keys edit the IP addresses.
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


        # Only handle roster keys on the player entry screen.
        if self.view.player_entry_screen:
            # Hardware ID box: type the number, Enter saves, Esc cancels.
            if self.view.hardware_popup:
                current = self.current_team_rows()[self.view.row]
                if event.key == pygame.K_ESCAPE:
                    self.view.hardware_popup = False
                    current["hardware_id"] = ""
                elif event.key == pygame.K_RETURN:
                    if current["hardware_id"]:
                        self.save_player(current)
                elif event.key == pygame.K_BACKSPACE:
                    current["hardware_id"] = current["hardware_id"][:-1]
                elif event.unicode.isdigit():
                    current["hardware_id"] += event.unicode
                return

            # Ask before removing a saved player for good.
            if self.pending_delete is not None:
                if event.key == pygame.K_y:
                    player_id = self.pending_delete
                    try:
                        deleted_player = self.model.delete_player(player_id)
                    except PlayerDatabaseError as error:
                        self.status = f"Database delete failed: {error}"
                    else:
                        self._refresh_added_rows()
                        self.status = (
                            f"Deleted player {deleted_player[0]} ({deleted_player[1]}) from database"
                        )
                    self.pending_delete = None
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.pending_delete = None
                    self.status = "Delete cancelled"
                return

            if event.key == pygame.K_F9:
                if self.current_player_needs_codename():
                    self.status = "Enter a valid name before leaving this player"
                    return
                self.network_source = self.udp.source_ip
                self.network_destination = self.udp.destination_ip
                self.network_field = 0
                self.view.network_screen = True
                return
            if event.key == pygame.K_F5:
                if any(
                    data["id"] and not self.is_valid_codename(data["codename"])
                    for team_rows in (self.model.red_rows, self.model.green_rows)
                    for data in team_rows
                ):
                    self.status = "Enter a valid name for every player ID before starting"
                    return
                self.view.player_entry_screen = False
                self.view.game_screen = True
                return

            if event.key == pygame.K_F12:
                self.model.clear_teams()
                self.added_rows.clear()
                self.view.row = 0
                self.view.col = 0
                self.status =  "Game cleared"
                return

            if event.key == pygame.K_UP:
                if self.current_player_needs_codename():
                    self.status = "Enter a valid name before moving to another row"
                    return
                self.view.row = max(0, self.view.row - 1)
                if not self.current_team_rows()[self.view.row]["id"]:
                    self.view.col = 0
                return
            if event.key == pygame.K_DOWN:
                if self.current_player_needs_codename():
                    self.status = "Enter a valid name before moving to another row"
                    return
                self.view.row = min(len(self.current_team_rows()) - 1, self.view.row + 1)
                if not self.current_team_rows()[self.view.row]["id"]:
                    self.view.col = 0
                return

            # Delete removes the saved player, not just the roster entry.
            if event.key == pygame.K_DELETE:
                rows = self.current_team_rows()
                current = rows[self.view.row]
                if current["id"] and current["codename"]:
                    self.pending_delete = current["id"]
                    self.status = (
                        f"Delete {current['id']} ({current['codename']}) from database? Y/N"
                    )
                else:
                    self.status = "Select a saved player to delete"
                return

            if event.key == pygame.K_TAB:
                current = self.current_team_rows()[self.view.row]
                if self.view.col == 0 and not current["id"]:
                    self.status = "Enter a Player ID first"
                    return
                self.view.col = 1 - self.view.col
                return

            # A dot switches the team being edited.
            if event.unicode == ".":
                if self.current_player_needs_codename():
                    self.status = "Enter a valid name before switching teams"
                    return
                self.view.current_team = "green" if self.view.current_team == "red" else "red"
                new_rows = self.current_team_rows()
                self.view.row = self.first_incomplete_row(new_rows)
                current = new_rows[self.view.row]
                self.view.col = 0 if not current["id"] else 1
                return

            rows = self.current_team_rows()
            current = rows[self.view.row]

            # Type the ID first, then move to the codename.
            if self.view.col == 0:
                if event.key == pygame.K_RETURN:
                    if current["id"]:
                        # Reject the ID if another spot in either team already uses it.
                        for team_rows in (self.model.red_rows, self.model.green_rows):
                            for data in team_rows:
                                if data is not current and data["id"] == current["id"]:
                                    self.status = "ID already in use"
                                    current["id"] = ""
                                    return
                        try:
                            current["codename"] = self.model.get_codename(current["id"]) or ""
                        except PlayerDatabaseError as error:
                            self.status = f"Database lookup failed: {error}"
                            return
                        self.view.col = 1
                elif event.key == pygame.K_BACKSPACE:
                    current["id"] = current["id"][:-1]
                elif event.unicode.isdigit() and len(current["id"]) < self.MAX_PLAYER_ID_LENGTH:
                    current["id"] += event.unicode

            # Type the codename, then Enter opens the hardware ID box.
            else:
                if not current["id"]:
                    self.view.col = 0
                    self.status = "Enter a Player ID first"
                    return
                if event.key == pygame.K_RETURN:
                    if current["id"] and self.is_valid_codename(current["codename"]):
                        self.view.hardware_popup = True
                    else:
                        self.status = "Name must be 1-15 characters with no spaces"
                elif event.key == pygame.K_BACKSPACE:
                    current["codename"] = current["codename"][:-1]
                elif (
                    event.unicode.isprintable()
                    and not event.unicode.isspace()
                    and len(current["codename"]) < self.MAX_CODENAME_LENGTH
                ):
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
