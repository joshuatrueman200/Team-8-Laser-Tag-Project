"""Run with: python3 -m unittest test_play_actions.py"""

import socket
import unittest
from types import SimpleNamespace

from play_actions import decode_hit, roster_by_hardware
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

    def test_friendly_fire(self):
        event = decode_hit(b"11:33\x00", self.players)
        self.assertEqual(event.label, "Opus --> Pal")
        self.assertTrue(event.friendly_fire)

    def test_base_hits_display_with_names(self):
        red_player_hit = decode_hit(b"11:43\x00", self.players)
        self.assertEqual(red_player_hit.label, "Opus --> Green Base")
        self.assertTrue(red_player_hit.base_hit)
        self.assertFalse(red_player_hit.friendly_fire)

        green_player_hit = decode_hit(b"22:53\x00", self.players)
        self.assertEqual(green_player_hit.label, "BigFoot --> Red Base")
        self.assertTrue(green_player_hit.base_hit)
        self.assertFalse(green_player_hit.friendly_fire)

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
