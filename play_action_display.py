"""Second Pygame window for live action. Countdown/images intentionally omitted."""

import pygame
from pygame._sdl2.video import Renderer, Texture, Window


class PlayActionDisplay:
    def __init__(self):
        # SDL2 permits a second real window without replacing the roster window.
        self.window = Window("Laser Tag - Play Action", size=(760, 580))
        self.renderer = Renderer(self.window)
        self.actions = []
        self.max_actions = 14
        self.textures = {}

    @property
    def window_id(self):
        return self.window.id

    def add_action(self, label):
        self.actions.append(label)
        self.actions = self.actions[-self.max_actions:]

    def _draw_text(self, message, x, y, size=28, color=(235, 235, 235)):
        key = (message, size, color)
        if key not in self.textures:
            font = pygame.font.Font(None, size)
            surface = font.render(message, True, color)
            self.textures[key] = Texture.from_surface(self.renderer, surface)
        texture = self.textures[key]
        self.renderer.blit(texture, pygame.Rect(x, y, texture.width, texture.height))

    def render(self):
        self.renderer.draw_color = (13, 16, 24, 255)
        self.renderer.clear()
        self._draw_text("PLAY ACTION", 30, 20, 44)
        self._draw_text("Live hits (shooter --> player or base)", 30, 67, 24, (170, 180, 195))

        self.draw_countdown_and_images()

        if not self.actions:
            self._draw_text("Waiting for tag events on UDP port 7501...", 30, 246, 26)
        else:
            for index, action in enumerate(reversed(self.actions)):
                self._draw_text(action, 36, 238 + index * 22, 23)
        self._draw_text("Close this window to stop the traffic generator", 30, 542,
                        21, (170, 180, 195))
        self.renderer.present()

    def draw_countdown_and_images(self):
        """TODO (teammate): add the 30-second countdown and images here.

        This reserved region is intentionally a placeholder: there is no
        running countdown or image sequence in this implementation.
        """
        placeholder = pygame.Rect(30, 105, 700, 100)
        self.renderer.draw_color = (90, 100, 118, 255)
        self.renderer.draw_rect(placeholder)
        self._draw_text("30-second countdown / image area", 52, 129, 27)
        self._draw_text("Placeholder: teammate will implement", 52, 164, 22,
                        (170, 180, 195))

    def close(self):
        # Destroy the renderer first, then its SDL2 window.
        self.textures.clear()
        self.renderer = None
        self.window.destroy()
