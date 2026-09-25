class Model():

    def __init__(self, player_database):
        self.player_database = player_database
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        for index, (player_id, codename) in enumerate(self.player_database.get_players()):
            if index >= len(self.red_rows):
                break
            self.red_rows[index] = {"id": str(player_id), "codename": codename}


    def clear_teams(self):
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        

    def add_player(self, player_id, codename):
        return self.player_database.add_player(player_id, codename)