"""Countdown tests that do not require a running display or PostgreSQL."""

from pathlib import Path
import unittest

from game_timer import GameTimer


class CountdownIntegrationTests(unittest.TestCase):
    def test_countdown_transitions_into_play(self):
        now = [100.0]
        timer = GameTimer(clock=lambda: now[0])
        timer.start()
        self.assertEqual(timer.phase, "countdown")
        self.assertEqual(timer.remaining(), 30)
        now[0] = 115.1
        timer.update()
        self.assertEqual(timer.remaining(), 15)
        now[0] = 130.0
        timer.update()
        self.assertEqual(timer.phase, "playing")
        self.assertEqual(timer.remaining(), 0)
        timer.reset()
        self.assertEqual(timer.phase, "idle")

    def test_all_countdown_frames_are_included(self):
        folder = Path(__file__).resolve().parent / "countdown_images"
        for seconds in range(31):
            with self.subTest(seconds=seconds):
                self.assertTrue((folder / f"countdown{seconds}.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
