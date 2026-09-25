class Model():

    def __init__(self, player_database):
        self.player_database = player_database
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]


    def clear_teams(self):
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        

    def add_player(self, player_id, codename):
        return self.player_database.add_player(player_id, codename)