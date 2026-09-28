# UDP Transport for Photon Equipment Coedes
import ipaddress
import socket


class UDPManager:
    def __init__(self, source_ip="127.0.0.1", destination_ip="127.0.0.1"):
        self.send_socket = None
        self.receive_socket = None
        self.change_network(source_ip, destination_ip)

    def change_network(self, source_ip, destination_ip):
        source_ip = str(ipaddress.IPv4Address(source_ip.strip()))
        destination_ip = str(ipaddress.IPv4Address(destination_ip.strip()))
        if source_ip.startswith("127.") != destination_ip.startswith("127."):
            raise ValueError("Localhost source and destination must both use 127.x.x.x")
        if self.send_socket and source_ip == self.source_ip:
            self.destination_ip = destination_ip
            return
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sender.bind((source_ip, 0))
            receiver.bind((source_ip, 7501))
            receiver.setblocking(False)
        except OSError:
            sender.close()
            receiver.close()
            raise
        old_sender, old_receiver = self.send_socket, self.receive_socket
        self.send_socket, self.receive_socket = sender, receiver
        self.source_ip, self.destination_ip = source_ip, destination_ip
        if old_sender:
            old_sender.close()
        if old_receiver:
            old_receiver.close()

    def broadcast_equipment_code(self, equipment_code):
        self.send_socket.sendto(str(equipment_code).encode("ascii"),
                                (self.destination_ip, 7500))

    def receive_messages(self):
        messages = []
        while True:
            try:
                data, address = self.receive_socket.recvfrom(4096)
            except BlockingIOError:
                return messages
            messages.append((data, address))

    def close(self):
        if self.send_socket:
            self.send_socket.close()
        if self.receive_socket:
            self.receive_socket.close()
