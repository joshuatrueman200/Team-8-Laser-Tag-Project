"""Second Pygame window for the countdown and live action."""

from pathlib import Path

import pygame
from pygame._sdl2.video import Renderer, Texture, Window

from game_timer import GameTimer


class PlayActionDisplay:
    def __init__(self):
        # SDL2 permits a second real window without replacing the roster window.
        self.window = Window("Laser Tag - Play Action", size=(760, 580))
        self.renderer = Renderer(self.window)
        self.actions = []
        self.max_actions = 14
        self.textures = {}

        # Use the teammate's countdown without changing the UDP/controller flow.
        self.game_timer = GameTimer()
        self.game_timer.start()
        self.countdown_texture = None
        self.countdown_frame = None

    @property
    def window_id(self):
        return self.window.id

    def add_action(self, label):
        # Incoming UDP events are still collected during the countdown.
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
        self.game_timer.update()
        self.renderer.draw_color = (13, 16, 24, 255)
        self.renderer.clear()

        if self.game_timer.phase == 'countdown':
            self.draw_countdown_and_images()
            self.renderer.present()
            return

        # Once the countdown finishes, return to the existing live-hit screen.
        self.countdown_texture = None
        self._draw_text("PLAY ACTION", 30, 20, 44)
        self._draw_text("Live hits (shooter --> player or base)", 30, 67, 24, (170, 180, 195))

        if not self.actions:
            self._draw_text("Waiting for tag events on UDP port 7501...", 30, 246, 26)
        else:
            for index, action in enumerate(reversed(self.actions)):
                self._draw_text(action, 36, 238 + index * 22, 23)
        self._draw_text("Close this window to stop the traffic generator", 30, 542,
                        21, (170, 180, 195))
        self.renderer.present()

    def draw_countdown_and_images(self):
        """Show the teammate's countdownN.jpg sequence in this second window."""
        seconds = max(0, min(30, self.game_timer.remaining()))
        if self.countdown_frame != seconds:
            image_path = Path(__file__).resolve().parent / "countdown_images" / f"countdown{seconds}.jpg"
            surface = pygame.image.load(str(image_path)).convert()
            surface = pygame.transform.smoothscale(surface, self.window.size)
            # Keep only the current image on the GPU (not all 31 large photos).
            self.countdown_texture = Texture.from_surface(self.renderer, surface)
            self.countdown_frame = seconds

        self.renderer.blit(self.countdown_texture, pygame.Rect((0, 0), self.window.size))

    def close(self):
        # Destroy the renderer first, then its SDL2 window.
        self.countdown_texture = None
        self.textures.clear()
        self.renderer = None
        self.window.destroy()
