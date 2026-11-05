"""Run with: python3 -m unittest test_play_actions.py"""

import socket
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from controller import Controller
from play_actions import decode_hit, hardware_ids_by_team, roster_by_hardware
from play_action_display import PlayActionDisplay
from tools.python_trafficgenarator_v2 import (
    create_test_event,
    fetch_roster,
    parse_roster_response,
)
from udp_manager import UDPManager


class PlayActionTests(unittest.TestCase):
    def setUp(self):
        self.model = SimpleNamespace(
            red_rows=[
                {"id": "1", "codename": "Opus", "hardware_id": "11"},
                {"id": "3", "codename": "Pal", "hardware_id": "33"},
            ],
            green_rows=[
                {"id": "2", "codename": "BigFoot", "hardware_id": "22"},
            ],
        )
        self.players = roster_by_hardware(self.model)

    def test_event_conversion(self):
        event = decode_hit(b"11:22\x00", self.players)
        self.assertEqual(event.label, "Opus --> BigFoot")
        self.assertFalse(event.friendly_fire)
        self.assertEqual(event.attacker_team, "red")

    def test_roster_hardware_ids_include_only_registered_players(self):
        model = SimpleNamespace(
            red_rows=self.model.red_rows + [
                {"id": "", "codename": "", "hardware_id": "44"},
            ],
            green_rows=self.model.green_rows + [
                {"id": "4", "codename": "", "hardware_id": "55"},
            ],
        )
        self.assertEqual(
            hardware_ids_by_team(model),
            {"red": ["11", "33"], "green": ["22"]},
        )

    def test_game_answers_local_roster_requests(self):
        replies = []
        controller = Controller.__new__(Controller)
        controller.model = self.model
        controller.udp = SimpleNamespace(
            receive_messages=lambda: [(b"ROSTER?", ("127.0.0.1", 7500))],
            send_roster=lambda roster, sender_ip: replies.append(
                (roster, sender_ip)
            ),
        )
        controller.action_display = None
        controller.game_started = False
        controller.network_destination = "127.0.0.1"
        controller.status = ""
        controller.view = SimpleNamespace(update=lambda: None)

        controller.update()

        self.assertEqual(
            replies,
            [
                (
                    {"red": ["11", "33"], "green": ["22"]},
                    "127.0.0.1",
                )
            ],
        )

    def test_traffic_generator_loads_roster_from_game_response(self):
        red_ids, green_ids = parse_roster_response(
            b'{"red":["11"],"green":["22","24"]}'
        )
        self.assertEqual(red_ids, ["11"])
        self.assertEqual(green_ids, ["22", "24"])

        class FakeSocket:
            def __init__(self):
                self.sent = []
                self.timeout = None
                self.timeout_history = []

            def settimeout(self, timeout):
                self.timeout = timeout
                self.timeout_history.append(timeout)

            def sendto(self, data, address):
                self.sent.append((data, address))

            def recvfrom(self, buffer_size):
                return b'{"red":["11"],"green":["22"]}', ("127.0.0.1", 7500)

        fake_socket = FakeSocket()
        self.assertEqual(fetch_roster(fake_socket), (["11"], ["22"]))
        self.assertEqual(fake_socket.sent[0][0], b"ROSTER?")
        self.assertEqual(fake_socket.timeout_history, [2, None])

    def test_traffic_generator_rejects_invalid_roster(self):
        with self.assertRaises(ValueError):
            parse_roster_response(b'{"red":["43"],"green":["22"]}')

    def test_friendly_fire(self):
        event = decode_hit(b"11:33\x00", self.players)
        self.assertEqual(event.label, "Opus --> Pal")
        self.assertTrue(event.friendly_fire)

    def test_base_hits_display_with_names(self):
        red_player_hit = decode_hit(b"11:43\x00", self.players)
        self.assertEqual(red_player_hit.label, "Opus --> Green Base")
        self.assertTrue(red_player_hit.base_hit)
        self.assertFalse(red_player_hit.friendly_fire)
        self.assertEqual(red_player_hit.attacker_team, "red")

        green_player_hit = decode_hit(b"22:53\x00", self.players)
        self.assertEqual(green_player_hit.label, "BigFoot --> Red Base")
        self.assertTrue(green_player_hit.base_hit)
        self.assertFalse(green_player_hit.friendly_fire)
        self.assertTrue(green_player_hit.scores_base)
        self.assertFalse(decode_hit(b"11:53\x00", self.players).scores_base)

    def test_scoring_player_hits_friendly_fire_and_opposing_bases(self):
        red_players = [
            {"name": "Opus", "hardware_id": "11", "score": 0, "base_scored": False},
            {"name": "Pal", "hardware_id": "33", "score": 0, "base_scored": False},
        ]
        green_players = [
            {"name": "BigFoot", "hardware_id": "22", "score": 0, "base_scored": False},
        ]
        display = object.__new__(PlayActionDisplay)
        display.team_rosters = {"red": red_players, "green": green_players}
        display.player_scores = {
            player["hardware_id"]: player
            for player in red_players + green_players
        }
        display.scores = {"red": 0, "green": 0}
        display.actions = []
        display.max_actions = 14

        display.add_hit(decode_hit(b"11:22\x00", self.players))
        self.assertEqual(red_players[0]["score"], 10)
        self.assertEqual(display.scores["red"], 10)

        display.add_hit(decode_hit(b"11:33\x00", self.players))
        self.assertEqual(red_players[0]["score"], 0)
        self.assertEqual(red_players[1]["score"], -10)
        self.assertEqual(display.scores["red"], -10)

        display.add_hit(decode_hit(b"11:43\x00", self.players))
        self.assertEqual(red_players[0]["score"], 100)
        self.assertTrue(red_players[0]["base_scored"])
        self.assertEqual(display.scores["red"], 90)

        display.add_hit(decode_hit(b"11:53\x00", self.players))
        self.assertEqual(red_players[0]["score"], 100)
        self.assertEqual(display.scores["red"], 90)

        display.add_hit(decode_hit(b"22:53\x00", self.players))
        self.assertEqual(green_players[0]["score"], 100)
        self.assertTrue(green_players[0]["base_scored"])
        self.assertEqual(display.scores["green"], 100)

    def test_traffic_generator_supports_uneven_rosters_and_friendly_fire(self):
        red_players = ["11"]
        green_players = ["22", "24"]
        with patch("tools.python_trafficgenarator_v2.random.choice",
                   side_effect=lambda values: values[0]):
            message, friendly_fire = create_test_event(
                red_players, green_players, 5
            )
        self.assertTrue(friendly_fire)
        self.assertEqual(message, "22:24")

    def test_traffic_generator_skips_friendly_fire_with_one_player_each(self):
        with patch("tools.python_trafficgenarator_v2.random.choice",
                   side_effect=lambda values: values[0]):
            message, friendly_fire = create_test_event(["11"], ["22"], 5)
        self.assertFalse(friendly_fire)
        self.assertIn(message, ("11:22", "22:11"))

    def test_traffic_generator_targets_opposing_bases(self):
        with patch("tools.python_trafficgenarator_v2.random.choice",
                   side_effect=lambda values: values[0]):
            red_message, _ = create_test_event(["11"], ["22"], 10)
            green_message, _ = create_test_event(["11"], ["22"], 20)
        self.assertEqual(red_message, "11:53")
        self.assertEqual(green_message, "22:43")

    def test_unknown_hardware_does_not_display_numbers(self):
        self.assertIsNone(decode_hit(b"11:999\x00", self.players))
        self.assertIsNone(decode_hit(b"999:43\x00", self.players))
        self.assertIsNone(decode_hit(b"garbage\x00", self.players))

    def test_base_hits_get_one_acknowledgment(self):
        manager = UDPManager()
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.settimeout(1)
        try:
            server.bind(("127.0.0.1", 7500))
            server.sendto(b"11:43\x00", ("127.0.0.1", 7501))
            packet, address = manager.receive_messages()[0]
            hit = decode_hit(packet, self.players)
            self.assertTrue(hit.base_hit)
            manager.acknowledge_hit(address[0], friendly_fire=hit.friendly_fire)
            self.assertEqual(server.recvfrom(1024)[0], b"201")
            with self.assertRaises(socket.timeout):
                server.recvfrom(1024)  # Base hits must not request the extra FF ACK.
        finally:
            server.close()
            manager.close()

    def test_receive_all_and_change_only_transmit_destination(self):
        manager = UDPManager()
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.settimeout(2)
        try:
            server.bind(("127.0.0.1", 7500))
            self.assertEqual(manager.receive_socket.getsockname(), ("0.0.0.0", 7501))
            manager.change_network("255.255.255.255")
            self.assertEqual(manager.destination_ip, "255.255.255.255")
            self.assertEqual(manager.receive_socket.getsockname(), ("0.0.0.0", 7501))
            manager.change_network("127.0.0.1")
            manager.start_game()
            self.assertEqual(server.recvfrom(1024)[0], b"202")

            server.sendto(b"11:33\x00", ("127.0.0.1", 7501))
            self.assertEqual(manager.receive_messages()[0][0], b"11:33\x00")
            manager.acknowledge_hit("127.0.0.1", friendly_fire=True)
            self.assertEqual(server.recvfrom(1024)[0], b"201")
            self.assertEqual(server.recvfrom(1024)[0], b"201")
        finally:
            server.close()
            manager.close()


if __name__ == "__main__":
    unittest.main()
