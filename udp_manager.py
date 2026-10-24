"""UDP transport for the equipment broadcaster and traffic generator."""

import ipaddress
import socket


class UDPManager:
    RECEIVE_PORT = 7501
    TRANSMIT_PORT = 7500

    def __init__(self, destination_ip="127.0.0.1"):
        # Receive on every local IPv4 interface, even after changing networks.
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.receive_socket.bind(("0.0.0.0", self.RECEIVE_PORT))
            self.receive_socket.setblocking(False)
            self.send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.change_network(destination_ip)
        except (ValueError, OSError):
            self.close()
            raise

    def change_network(self, destination_ip):
        """Change only the destination for outgoing packets, not the listening IP."""
        address = ipaddress.IPv4Address(destination_ip.strip())
        if address.is_unspecified:
            raise ValueError("0.0.0.0 is for receiving, not transmitting")
        self.destination_ip = str(address)

    def send_message(self, message, destination_ip=None):
        ip = destination_ip if destination_ip is not None else self.destination_ip
        self.send_socket.sendto(str(message).encode("ascii"), (ip, self.TRANSMIT_PORT))

    def broadcast_equipment_code(self, equipment_code):
        self.send_message(equipment_code)

    def start_game(self):
        # The provided traffic generator does not start until it receives 202.
        self.send_message("202")

    def acknowledge_hit(self, sender_ip, friendly_fire=False):
        # Its listener is at port 7500, NOT the ephemeral transmit port.
        self.send_message("201", sender_ip)
        if friendly_fire:
            # The generator waits for one additional response for friendly fire.
            self.send_message("201", sender_ip)

    def stop_game(self, sender_ip=None):
        # The generator stops upon receiving 221 as a hit response.
        self.send_message("221", sender_ip)

    def receive_messages(self):
        messages = []
        while True:
            try:
                data, address = self.receive_socket.recvfrom(4096)
            except BlockingIOError:
                return messages
            messages.append((data, address))

    def close(self):
        if getattr(self, "send_socket", None) is not None:
            self.send_socket.close()
            self.send_socket = None
        if getattr(self, "receive_socket", None) is not None:
            self.receive_socket.close()
            self.receive_socket = None
