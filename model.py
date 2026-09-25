from database import PlayerDatabaseError


class Model():

    def __init__(self, player_database):
        self.player_database = player_database
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.database_players = {}
        for index, (player_id, codename) in enumerate(self.player_database.get_players()):
            if index >= len(self.red_rows):
                break
            player_id = str(player_id)
            self.database_players[player_id] = codename
            self.red_rows[index] = {"id": player_id, "codename": codename}


    def clear_teams(self):
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        

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

        if team == "red":
            other_rows = self.green_rows
        else:
            other_rows = self.red_rows
        for index, data in enumerate(other_rows):
            if data["id"] == player_id:
                other_rows[index] = {"id": "", "codename": ""}

        return is_new_player