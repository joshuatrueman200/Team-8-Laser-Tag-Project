"""Second Pygame window for the countdown and live action."""

from pathlib import Path

import pygame
from pygame._sdl2.video import Renderer, Texture, Window

from game_timer import GameTimer


class PlayActionDisplay:
    def __init__(self, team_rosters=None):
        # SDL2 permits a second real window without replacing the roster window.
        self.window = Window("Laser Tag - Play Action", size=(760, 580))
        self.renderer = Renderer(self.window)
        self.actions = []
        self.max_actions = 14
        self.textures = {}
        self.team_rosters = team_rosters or {"red": [], "green": []}
        self.scores = {"red": 0, "green": 0}

        # Use the teammate's countdown without changing the UDP/controller flow.
        self.game_timer = GameTimer(game_duration_seconds=360)
        self.game_timer.start()
        self.countdown_texture = None
        self.countdown_frame = None

    def add_score(self, team):
        if team in self.scores:
            self.scores[team] += 1

    @property
    def window_id(self):
        return self.window.id

    def add_action(self, label):
        # Keep the existing event feed available while the countdown is visible.
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

        if self.game_timer.phase == 'countdown':
            self.draw_countdown_and_images()
            self.renderer.present()
            return
        if self.game_timer.phase == 'finished':
            self.draw_game_over()
            self.renderer.present()
            return

        self.countdown_texture = None
        self._draw_text("PLAY ACTION", 30, 20, 44)
        self._draw_text("TEAMS", 30, 70, 24, (170, 180, 195))
        self._draw_team("red", 30, 95, (255, 100, 100))
        self._draw_team("green", 395, 95, (100, 230, 130))
        self._draw_text("LIVE HITS (shooter --> player or base)", 30, 270, 22,
                        (170, 180, 195))

        if not self.actions:
            self._draw_text("Waiting for tag events on UDP port 7501...", 30, 310, 23)
        else:
            for index, action in enumerate(reversed(self.actions[-10:])):
                self._draw_text(action, 36, 310 + index * 22, 21)
        self._draw_text("Close this window to stop the traffic generator", 30, 542,
                        21, (170, 180, 195))
        self.renderer.present()

    def draw_game_over(self):
        winner = self._winning_team()
        self._draw_text("GAME OVER", 30, 24, 48)
        if winner == "tie":
            result = "FINAL RESULT: TIE"
        else:
            result = f"WINNER: {winner.upper()} TEAM"
        self._draw_text(result, 30, 82, 32, (255, 220, 100))
        self._draw_team("red", 30, 155, (255, 100, 100))
        self._draw_team("green", 395, 155, (100, 230, 130))

    def _winning_team(self):
        if self.scores["red"] == self.scores["green"]:
            return "tie"
        return "red" if self.scores["red"] > self.scores["green"] else "green"

    def _draw_team(self, team, x, y, color):
        label = "RED TEAM" if team == "red" else "GREEN TEAM"
        self._draw_text(f"{label}  Score: {self.scores[team]}", x, y, 26, color)
        players = self.team_rosters[team]
        if not players:
            self._draw_text("No players registered", x, y + 34, 20)
            return

        split = (len(players) + 1) // 2
        for index, player in enumerate(players):
            column = index // split
            row = index % split
            self._draw_text(f"{index + 1}. {player}",
                            x + column * 175, y + 36 + row * 17, 18)

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
