import socket
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.protocol import build_packet
from shared.packet_ids import PacketID

def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Server disconnected")
        data += chunk
    return data

def read_packet(sock):
    (length,) = struct.unpack("!I", recv_exact(sock, 4))
    body = recv_exact(sock, length)
    packet_id = struct.unpack("!H", body[:2])[0]
    return packet_id, body[2:]

class GameClient:
    def __init__(self, host="127.0.0.1", port=9000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        print("[+] Connected to GameService")

    def send(self, packet_id, payload: str | bytes):
        self.sock.sendall(build_packet(packet_id, payload))

    def recv(self):
        return read_packet(self.sock)

    def close(self):
        self.sock.close()

if __name__ == "__main__":
    client = GameClient()

    # Receive all 4 intro packets from server
    for _ in range(4):
        packet_id, payload = client.recv()
        print(f"[RECV] {PacketID(packet_id).name}: {payload.decode()}")

    # Keep connection alive
    print("\nCommands: ping, quit")
    while True:
        try:
            cmd = input("> ").strip().lower()

            if cmd == "ping":
                client.send(PacketID.PING, b"PING")
                packet_id, payload = client.recv()
                print(f"[RECV] {PacketID(packet_id).name}: {payload.decode()}")

            elif cmd == "quit":
                break

            else:
                print("Unknown command")

        except KeyboardInterrupt:
            break

    client.close()
    print("[+] Disconnected")
