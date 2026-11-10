import unittest
from unittest.mock import patch

from game_audio import GameAudio


class GameAudioTests(unittest.TestCase):
    @patch("game_audio.pygame.mixer.music")
    @patch("game_audio.random.choice")
    def test_countdown_plays_a_random_available_track(self, choose_track, music):
        audio = GameAudio()
        available_tracks = sorted(
            audio.asset_directory.glob(audio.COUNTDOWN_TRACK_PATTERN)
        )
        self.assertTrue(available_tracks)
        choose_track.return_value = available_tracks[-1]

        audio.play_countdown()

        choose_track.assert_called_once_with(available_tracks)
        music.load.assert_called_once_with(str(available_tracks[-1]))
        music.set_volume.assert_called_once_with(1)
        music.play.assert_called_once_with()

    @patch("game_audio.pygame.mixer.music")
    def test_music_off_disables_countdown_audio(self, music):
        GameAudio(enabled=False).play_countdown()

        music.load.assert_not_called()
        music.play.assert_not_called()


if __name__ == "__main__":
    unittest.main()
