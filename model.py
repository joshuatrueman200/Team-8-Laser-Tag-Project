import pygame
import sqlite3

class Player():
    def __init__(self, id, code_name, team):
        self.id = id
        self.code_name = code_name
        self.team = team

class Model():

    def __init__(self, db_conection):
        self.db_conection = db_conection
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]


    def clear_teams(self):
        self.red_rows = [{"id": "", "codename": ""} for _ in range(15)]
        self.green_rows = [{"id": "", "codename": ""} for _ in range(15)]
        

#############################################
############### DB Connection HERE 
# Feel free to change the code .- Eduardo
    def create_player_db(self):
        conn = sqlite3.connect("player.db")

        with open("player.sql", "r") as f:
            sql = f.read()

        conn.executescript(sql)
        conn.commit()
        conn.close()


    def check_ID_DB(self, id):
        print(id)

    def check_Codename_DB(self, codename):
        print(codename)