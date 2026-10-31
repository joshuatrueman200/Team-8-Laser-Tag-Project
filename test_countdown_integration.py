"""Countdown tests that do not require a running display or PostgreSQL."""

from pathlib import Path
import unittest
from types import SimpleNamespace

import pygame

from controller import Controller
from game_timer import GameTimer


class CountdownIntegrationTests(unittest.TestCase):
    def test_controller_requires_a_player_on_each_team_before_start(self):
        blank_team = [
            {"id": "", "codename": "", "hardware_id": ""}
            for _ in range(15)
        ]
        controller = Controller.__new__(Controller)
        controller.model = SimpleNamespace(
            red_rows=blank_team,
            green_rows=[row.copy() for row in blank_team],
        )
        controller.view = SimpleNamespace(
            network_screen=False,
            player_entry_screen=True,
            hardware_popup=False,
            row=0,
            current_team="red",
        )
        controller.pending_delete = None
        controller.action_display = None
        controller.status = ""

        controller.handle_event(
            SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_F5, unicode="")
        )

        self.assertEqual(
            controller.status,
            "Add at least one player to each team before starting",
        )
        self.assertIsNone(controller.action_display)

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

    def test_six_minute_game_starts_after_countdown_and_expires(self):
        now = [100.0]
        timer = GameTimer(
            countdown_seconds=30,
            clock=lambda: now[0],
            game_duration_seconds=360,
        )
        timer.start()

        now[0] = 129.0
        timer.update()
        self.assertEqual(timer.phase, "countdown")
        self.assertEqual(timer.remaining(), 1)

        now[0] = 130.0
        timer.update()
        self.assertEqual(timer.phase, "playing")
        self.assertEqual(timer.remaining(), 360)
        self.assertEqual(timer.formatted(), "06:00")

        now[0] = 250.0
        timer.update()
        self.assertEqual(timer.remaining(), 240)
        self.assertEqual(timer.formatted(), "04:00")

        now[0] = 490.0
        timer.update()
        self.assertEqual(timer.phase, "finished")
        self.assertEqual(timer.remaining(), 0)

    def test_controller_starts_and_stops_generator_at_timer_boundaries(self):
        now = [100.0]
        timer = GameTimer(
            countdown_seconds=30,
            clock=lambda: now[0],
            game_duration_seconds=360,
        )
        timer.start()

        class FakeDisplay:
            game_timer = timer
            scores = {"red": 4, "green": 2}

            def render(self):
                pass

        class FakeUDP:
            def __init__(self):
                self.start_count = 0
                self.stops = []

            def start_game(self):
                self.start_count += 1

            def stop_game(self, sender):
                self.stops.append(sender)

            def receive_messages(self):
                return []

        view = SimpleNamespace(
            game_timer_label="",
            game_final_score=None,
            game_in_progress=True,
            network_destination="127.0.0.1",
            status="",
            update=lambda: None,
        )
        controller = Controller.__new__(Controller)
        controller.action_display = FakeDisplay()
        controller.action_roster = {}
        controller.game_started = False
        controller.game_over_handled = False
        controller.last_traffic_sender = None
        controller.network_destination = "127.0.0.1"
        controller.status = ""
        controller.udp = FakeUDP()
        controller.view = view

        now[0] = 129.0
        controller.update()
        self.assertEqual(controller.udp.start_count, 0)
        self.assertEqual(view.game_timer_label, "GAME STARTS IN 00:01")

        now[0] = 130.0
        controller.update()
        self.assertEqual(controller.udp.start_count, 1)
        self.assertEqual(view.game_timer_label, "GAME TIME 06:00")

        now[0] = 490.0
        controller.update()
        self.assertEqual(controller.udp.stops, [None])
        self.assertEqual(view.game_final_score, (4, 2))
        self.assertTrue(controller.game_over_handled)

    def test_all_countdown_frames_are_included(self):
        folder = Path(__file__).resolve().parent / "countdown_images"
        for seconds in range(31):
            with self.subTest(seconds=seconds):
                self.assertTrue((folder / f"countdown{seconds}.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
