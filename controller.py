import pygame

class Controller():

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def handle_event(self, event):
        pass

    def update(self):
        self.view.update()