import asyncio
import struct
from shared.packet_ids import PacketID
from shared.protocol import build_packet

async def read_exact(reader, size):
    data = b""
    while len(data) < size:
        chunk = await reader.read(size - len(data))
        if not chunk:
            raise ConnectionError("Disconnected")
        data += chunk
    return data

async def read_packet(reader):
    length_data = await read_exact(reader, 4)
    (length,) = struct.unpack("!I", length_data)
    body = await read_exact(reader, length)
    packet_id = struct.unpack("!H", body[:2])[0]
    payload = body[2:].decode("utf-8")
    return packet_id, payload

class GameServiceClient:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.addr = writer.get_extra_info("peername")

    async def handle(self):
        print(f"[+] Client connected: {self.addr}")
        await self.send(PacketID.MOTD,      "Welcome to the MMO Server!")
        await self.send(PacketID.IRIS,      "Iris Loves You")
        await self.send(PacketID.INVENTORY, "Starter Sword")
        await self.send(PacketID.AIDAN,     "Aidan Loves Iris")

        try:
            while True:
                packet_id, payload = await read_packet(self.reader)
                await self.dispatch(packet_id, payload)
        except Exception as e:
            print(f"[-] Client disconnected: {self.addr} ({e})")
        finally:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass  # client already gone, ignore cleanup errors

    async def dispatch(self, packet_id, payload):
        if packet_id == PacketID.PING:
            print(f"[RECV] PING from {self.addr}")
            await self.send(PacketID.PING, "PONG")
        else:
            print(f"[RECV] Packet {packet_id}: {payload}")

    async def send(self, packet_id, payload):
        self.writer.write(build_packet(packet_id, payload))
        await self.writer.drain()
        print(f"[SEND] {PacketID(packet_id).name} -> {self.addr}")

async def start_server():
    server = await asyncio.start_server(
        lambda r, w: GameServiceClient(r, w).handle(),
        "127.0.0.1", 9000
    )
    print("🚀 MMO Server running on 127.0.0.1:9000")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(start_server())