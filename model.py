from database import PlayerDatabaseError

TEAM_SIZE = 15


class Model:
    # Hold the team lists and talk to the database.

    def __init__(self, player_database):
        self.player_database = player_database
        self.red_rows = self._empty_team()
        self.green_rows = self._empty_team()
        self.database_players = {}
        for index, (player_id, codename) in enumerate(self.player_database.get_players()):
            player_id = str(player_id)
            self.database_players[player_id] = codename
            if index < len(self.red_rows):
                self.red_rows[index] = {"id": player_id, "codename": codename}

    @staticmethod
    def _empty_team():
        # Give each team 15 blank spots.
        return [{"id": "", "codename": ""} for _ in range(TEAM_SIZE)]

    def clear_teams(self):
        # Clear this game's lists, not the database.
        self.red_rows = self._empty_team()
        self.green_rows = self._empty_team()

    def add_player(self, player_id, codename, team):
        player_id = str(player_id)
        if team not in ("red", "green"):
            raise ValueError(f"Unknown team: {team}")

        existing_codename = self.database_players.get(player_id)
        is_new_player = existing_codename is None
        if not is_new_player and existing_codename != codename:
            raise PlayerDatabaseError(
                f"Player ID {player_id} is already registered as {existing_codename}"
            )
        if is_new_player:
            self.player_database.add_player(player_id, codename)
            self.database_players[player_id] = codename

        # Keep a player on just one team.
        if team == "red":
            other_rows = self.green_rows
        else:
            other_rows = self.red_rows
        for index, data in enumerate(other_rows):
            if data["id"] == player_id:
                other_rows[index] = {"id": "", "codename": ""}

        return is_new_player

    def delete_player(self, player_id):
        # Delete from the database before clearing the screen.
        player_id = str(player_id)
        if player_id not in self.database_players:
            raise PlayerDatabaseError(f"Player ID {player_id} is not saved in the database")

        deleted_player = self.player_database.delete_player(player_id)
        if deleted_player is None:
            raise PlayerDatabaseError(f"Player ID {player_id} was not found in the database")

        self.database_players.pop(player_id, None)
        for rows in (self.red_rows, self.green_rows):
            for index, data in enumerate(rows):
                if data["id"] == player_id:
                    rows[index] = {"id": "", "codename": ""}
        return deleted_player