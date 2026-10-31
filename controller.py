import pygame
from database import PlayerDatabaseError
from udp_manager import UDPManager
from play_actions import BASE_TARGETS, decode_hit, roster_by_hardware
from play_action_display import PlayActionDisplay


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
        self.network_destination = self.udp.destination_ip
        self.action_display = None
        self.action_roster = {}
        self.game_started = False
        self.game_over_handled = False
        self.last_traffic_sender = None
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

    def current_player_is_incomplete(self):
        current = self.current_team_rows()[self.view.row]
        return bool(current["id"]) and (
            not self.is_valid_codename(current["codename"])
            or not current["hardware_id"]
        )

    def save_player(self, current):
        # Save the player; the hardware ID stays in the team row. Then go to the next row.
        # Base equipment IDs are not available for player registration.
        if current["hardware_id"] in BASE_TARGETS:
            base_name = BASE_TARGETS[current["hardware_id"]]
            self.status = f"Hardware ID is reserved for {base_name}"
            return
        # Each registered player must have a different piece of equipment.
        for team_rows in (self.model.red_rows, self.model.green_rows):
            for row in team_rows:
                if row is not current and row["hardware_id"] == current["hardware_id"]:
                    self.status = "Hardware ID is already assigned to another player"
                    return
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

        # Transmit the equipment code that was just entered, not the player ID.
        try:
            self.udp.broadcast_equipment_code(current["hardware_id"])
        except OSError as error:
            self.status = f"Player saved, but UDP transmission failed: {error}"

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

        # F9 edits only where UDP transmissions are sent. Reception always
        # stays bound to 0.0.0.0:7501 (all local IPv4 interfaces).
        if self.view.network_screen:
            if event.key == pygame.K_ESCAPE:
                self.view.network_screen = False
                return
            if event.key == pygame.K_RETURN:
                try:
                    self.udp.change_network(self.network_destination)
                except ValueError as error:
                    self.status = f"Network error: {error}"
                else:
                    self.status = f"Sending UDP to {self.udp.destination_ip}:7500"
                    self.view.network_screen = False
                return
            if event.key == pygame.K_BACKSPACE:
                self.network_destination = self.network_destination[:-1]
            elif event.unicode and event.unicode in "0123456789.":
                if len(self.network_destination) < 15:
                    self.network_destination += event.unicode
            return

        # ESC pressed in the additional window ends play, without closing
        # the roster window (the window close button is also supported).
        if self.action_display is not None and event.key == pygame.K_ESCAPE:
            if self.is_action_window_event(event):
                self.stop_play_action()
            return
        if self.is_action_window_event(event):
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
                if self.current_player_is_incomplete():
                    self.status = "Finish the name and hardware ID before leaving this player"
                    return
                self.network_destination = self.udp.destination_ip
                self.view.network_screen = True
                return
            if event.key == pygame.K_F5:
                if any(
                    data["id"] and (
                        not self.is_valid_codename(data["codename"])
                        or not data["hardware_id"]
                    )
                    for team_rows in (self.model.red_rows, self.model.green_rows)
                    for data in team_rows
                ):
                    self.status = "Finish the name and hardware ID for every player before starting"
                    return
                if self.action_display is not None:
                    self.action_display.window.focus()
                    phase = self.action_display.game_timer.phase
                    if phase == "finished":
                        self.status = "Game is over; showing the final scoreboard"
                    elif phase == "playing":
                        self.status = "Game is in progress; showing Play Action"
                    else:
                        self.status = "Game countdown is in progress"
                    return
                try:
                    team_rosters = {
                        team: [
                            data["codename"]
                            for data in rows
                            if data["id"] and data["codename"]
                        ]
                        for team, rows in (
                            ("red", self.model.red_rows),
                            ("green", self.model.green_rows),
                        )
                    }
                    self.action_display = PlayActionDisplay(team_rosters)
                    self.action_roster = roster_by_hardware(self.model)
                    self.last_traffic_sender = None
                    self.game_started = False
                    self.game_over_handled = False
                    self.view.game_final_score = None
                    self.view.game_in_progress = True
                except (OSError, pygame.error, ImportError) as error:
                    self.status = f"Unable to start play action: {error}"
                    if self.action_display is not None:
                        self.action_display.close()
                        self.action_display = None
                else:
                    self.status = "Play action countdown started; game begins in 30 seconds"
                return

            if event.key == pygame.K_F12:
                self.model.clear_teams()
                self.added_rows.clear()
                self.view.row = 0
                self.view.col = 0
                self.status =  "Game cleared"
                return

            if event.key == pygame.K_UP:
                if self.current_player_is_incomplete():
                    self.status = "Finish the name and hardware ID before moving to another row"
                    return
                self.view.row = max(0, self.view.row - 1)
                if not self.current_team_rows()[self.view.row]["id"]:
                    self.view.col = 0
                return
            if event.key == pygame.K_DOWN:
                if self.current_player_is_incomplete():
                    self.status = "Finish the name and hardware ID before moving to another row"
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
                if self.current_player_is_incomplete():
                    self.status = "Finish the name and hardware ID before switching teams"
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

    def is_action_window_event(self, event):
        """SDL2 associates input/close events with the actual Window object."""
        if self.action_display is None:
            return False
        event_window = getattr(event, "window", None)
        return event_window in (self.action_display.window,
                                self.action_display.window_id)

    def stop_play_action(self):
        if self.action_display is None:
            return
        # Stop the traffic generator with its expected termination message.
        if self.game_started:
            try:
                self.udp.stop_game(self.last_traffic_sender)
            except OSError as error:
                self.status = f"Could not signal game stop: {error}"
            else:
                self.status = "Play action closed"
        else:
            self.status = "Play action closed before game start"
        self.action_display.close()
        self.action_display = None
        self.action_roster = {}
        self.game_started = False
        self.game_over_handled = False
        self.last_traffic_sender = None
        self.view.game_timer_label = ""
        self.view.game_in_progress = False

    def update(self):
        if self.action_display is not None:
            self.action_display.game_timer.update()
            phase = self.action_display.game_timer.phase
            if phase == "countdown":
                self.view.game_timer_label = (
                    f"GAME STARTS IN {self.action_display.game_timer.formatted()}"
                )
            elif phase == "playing":
                self.view.game_timer_label = (
                    f"GAME TIME {self.action_display.game_timer.formatted()}"
                )
            if (
                phase == "playing"
                and not self.game_started
            ):
                try:
                    self.udp.start_game()
                except OSError as error:
                    self.status = f"Unable to start traffic generator: {error}"
                    self.action_display.close()
                    self.action_display = None
                    self.action_roster = {}
                    self.last_traffic_sender = None
                    self.view.game_timer_label = ""
                    self.view.game_in_progress = False
                else:
                    self.game_started = True
                    self.status = "Play action started; listening for tag events on UDP 7501"
            elif phase == "finished" and not self.game_over_handled:
                if self.game_started:
                    try:
                        self.udp.stop_game(self.last_traffic_sender)
                    except OSError as error:
                        self.status = f"Game ended, but could not stop traffic generator: {error}"
                    else:
                        self.status = "Game over"
                else:
                    self.status = "Game over"
                self.game_started = False
                self.game_over_handled = True
                self.view.game_timer_label = ""
                self.view.game_final_score = (
                    self.action_display.scores["red"],
                    self.action_display.scores["green"],
                )
                self.view.status = self.status

        for data, address in self.udp.receive_messages():
            if self.action_display is None or not self.game_started:
                print(f"UDP received from {address}: {data!r}")
                continue
            hit = decode_hit(data, self.action_roster)
            if hit is not None:
                self.action_display.add_action(hit.label)
                self.action_display.add_score(hit.attacker_team)
                print(f"TAG: {hit.label}")
            else:
                # Ignore malformed packets and unknown hardware IDs.
                # Known base targets (43/53) are displayed by decode_hit().
                print(f"Ignoring non-player tag packet: {data!r}")
            # Acknowledge any well-formed generator event. Even hits to a
            # base must get a reply so the generator can continue.
            try:
                payload = data.decode("utf-8").rstrip("\x00")
                ids = payload.split(":")
            except UnicodeDecodeError:
                continue
            if len(ids) != 2 or not all(value.isdecimal() for value in ids):
                continue
            self.last_traffic_sender = address[0]
            try:
                self.udp.acknowledge_hit(address[0],
                                         friendly_fire=hit.friendly_fire if hit else False)
            except OSError as error:
                self.status = f"UDP acknowledgment error: {error}"

        self.view.network_destination = self.network_destination
        self.view.status = self.status
        self.view.update()
        if self.action_display is not None:
            self.action_display.render()

    def close(self):
        if self.action_display is not None:
            self.stop_play_action()
        self.udp.close()
