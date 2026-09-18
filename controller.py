import pygame

class Controller():

    def __init__(self, model, view):
        self.model = model
        self.view = view
    #Keybard inputs
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            if self.view.player_entry_screen:
                self.view.player_entry_screen = False
                self.view.game_screen = True
            

    def update(self):
        self.view.update()