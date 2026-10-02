from database import PlayerDatabaseError

TEAM_SIZE = 15


class Model:
    # Hold the team lists and talk to the database.

    def __init__(self, player_database):
        self.player_database = player_database
        self.red_rows = self._empty_team()
        self.green_rows = self._empty_team()
        self.database_players = {}
        for player_id, codename in self.player_database.get_players():
            self.database_players[str(player_id)] = codename

    @staticmethod
    def _empty_team():
        # Give each team 15 blank spots.
        return [{"id": "", "codename": ""} for _ in range(TEAM_SIZE)]

    def clear_teams(self):
        # Clear this game's lists, not the database.
        self.red_rows = self._empty_team()
        self.green_rows = self._empty_team()

    def get_codename(self, player_id):
        player_id = str(player_id)
        player = self.player_database.get_player(player_id)
        if player is None:
            self.database_players.pop(player_id, None)
            return None

        saved_id, codename = player
        saved_id = str(saved_id)
        self.database_players[saved_id] = codename
        return codename

    def add_player(self, player_id, codename, team):
        player_id = str(player_id)
        if team not in ("red", "green"):
            raise ValueError(f"Unknown team: {team}")

        existing_codename = self.database_players.get(player_id)
        is_new_player = player_id not in self.database_players
        if is_new_player:
            self.player_database.add_player(player_id, codename)
        elif existing_codename != codename:
            self.player_database.update_codename(player_id, codename)
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

    def clear_codenames(self):
        cleared_players = self.player_database.clear_codenames()
        for player_id, _ in cleared_players:
            player_id = str(player_id)
            self.database_players[player_id] = ""
            for rows in (self.red_rows, self.green_rows):
                for data in rows:
                    if data["id"] == player_id:
                        data["codename"] = ""
        return len(cleared_players)

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