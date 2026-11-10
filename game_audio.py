"""Audio playback for the background music and game countdown."""

import random
from pathlib import Path

import pygame


class GameAudio:
    BACKGROUND_TRACK = "photon_tracks_Track01.mp3"
    COUNTDOWN_TRACK_PATTERN = "photon_tracks_Track*.mp3"

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.asset_directory = Path(__file__).resolve().parent / "Asset"

    def play_background(self):
        if not self.enabled:
            return

        track = self.asset_directory / self.BACKGROUND_TRACK
        pygame.mixer.music.load(str(track))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1, start=180)

    def play_countdown(self):
        if not self.enabled:
            return

        tracks = sorted(self.asset_directory.glob(self.COUNTDOWN_TRACK_PATTERN))
        if not tracks:
            raise FileNotFoundError(
                f"No countdown audio tracks found in {self.asset_directory}"
            )

        pygame.mixer.music.load(str(random.choice(tracks)))
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()
