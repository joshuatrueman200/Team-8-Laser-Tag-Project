import pygame

class Player():
    def __init__(self, id, code_name, team):
        self.id = id
        self.code_name = code_name
        self.team = team

class Model():

    def __init__(self, db_conection):
        self.db_conection = db_conection

#############################################
############### DB Connection HERE 
# Feel free to change the code .- Eduardo
    def check_ID_DB(self, id):
        pass

    def check_Codename_DB(self, codename):
        pass