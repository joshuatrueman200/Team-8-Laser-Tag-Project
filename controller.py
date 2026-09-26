import pygame
from database import PlayerDatabaseError
from udp_manager import UDPManager


class Controller:
    # Turn key presses into game, database, and network actions.

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

    def _current_team_rows(self):
        # Return the list for the team on screen.
        if self.view.current_team == "red":
            return self.model.red_rows
        return self.model.green_rows

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
                self.network_source = self.udp.source_ip
                self.network_destination = self.udp.destination_ip
                self.network_field = 0
                self.view.network_screen = True
                return
            if event.key == pygame.K_F5:
                self.view.player_entry_screen = False
                self.view.game_screen = True
                return

            if event.key == pygame.K_F12:
                self.model.clear_teams()
                self.added_rows.clear()
                self.view.row = 0
                self.view.col = 0
                self.status = "Roster cleared from screen only; database unchanged"
                return

            if event.key == pygame.K_UP:
                self.view.row = max(0, self.view.row - 1)
                return
            if event.key == pygame.K_DOWN:
                self.view.row = min(len(self._current_team_rows()) - 1, self.view.row + 1)
                return

            # Delete removes the saved player, not just the roster entry.
            if event.key == pygame.K_DELETE:
                rows = self._current_team_rows()
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
                self.view.col = 1 - self.view.col
                return

            # A dot switches the team being edited.
            if event.unicode == ".":
                self.view.current_team = "green" if self.view.current_team == "red" else "red"
                new_rows = self._current_team_rows()
                self.view.row = self.first_incomplete_row(new_rows)
                current = new_rows[self.view.row]
                self.view.col = 0 if not current["id"] else 1
                return

            rows = self._current_team_rows()
            current = rows[self.view.row]

            # Type the ID first, then move to the codename.
            if self.view.col == 0:
                if event.key == pygame.K_RETURN:
                    if current["id"]:
                        self.view.col = 1
                elif event.key == pygame.K_BACKSPACE:
                    current["id"] = current["id"][:-1]
                elif event.unicode.isdigit():
                    current["id"] += event.unicode

            # Type the codename, then Enter saves or assigns the player.
            else:
                if event.key == pygame.K_RETURN:
                    if current["id"] and current["codename"]:
                        key = (self.view.current_team, self.view.row)
                        if key not in self.added_rows:
                            try:
                                is_new_player = self.model.add_player(
                                    current["id"], current["codename"], self.view.current_team
                                )
                            except PlayerDatabaseError as error:
                                self.status = f"Database save failed: {error}"
                                return
                            self._refresh_added_rows()
                            if is_new_player:
                                self.status = (
                                    f"Saved player {current['id']} ({current['codename']}) "
                                    f"to database and assigned to {self.view.current_team}"
                                )
                            else:
                                self.status = (
                                    f"Assigned player {current['id']} ({current['codename']}) "
                                    f"to {self.view.current_team}"
                                )
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
