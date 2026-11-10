"""Play the game-start audio track."""

from pathlib import Path

import pygame


class GameAudio:
    GAME_START_TRACK = "photon_tracks_Track01.mp3"

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.asset_directory = Path(__file__).resolve().parent / "Asset"

    def play_game_start(self):
        if not self.enabled:
            return

        track = self.asset_directory / self.GAME_START_TRACK
        pygame.mixer.music.load(str(track))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()
