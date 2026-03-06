import asyncio
import websockets
import sys
import signal

from PythonProject.WebsocketMMO.Server.common import messagepack_utils, packet_types


class MMOClient:
    def __init__(self, host="localhost", port=9100):
        self.host = host
        self.port = port
        self.ws = None
        self.running = True

    async def connect(self):
        try:
            self.ws = await websockets.connect(f"ws://{self.host}:{self.port}")
            print(f"[Client] Connected to WorldServer at {self.host}:{self.port}")
        except Exception as e:
            print(f"[Client] Connection failed: {e}")
            self.running = False

    async def send_message(self, opcode, payload, request_id=0):
        if self.ws:
            packet = messagepack_utils.pack_packet(opcode, request_id=request_id, payload=payload)
            await self.ws.send(packet)

    async def handle_server_messages(self):
        try:
            async for msg in self.ws:
                packet = messagepack_utils.unpack_packet(msg)
                await self.handle_packet(packet)
        except websockets.ConnectionClosed:
            print("[Client] Disconnected from WorldServer")
            self.running = False

    async def handle_packet(self, packet):
        opcode = packet.get("opcode")
        if opcode == packet_types.EPacketOpcode.MOTD:
            print(f"[MOTD] {packet.get('payload')}")
        elif opcode == packet_types.EPacketOpcode.WORLD_EVENT:
            print(f"[World Event] {packet.get('payload')}")
        elif opcode == packet_types.EPacketOpcode.SERVER_MESSAGE:
            print(f"[Server Message] {packet.get('payload')}")
        else:
            print(f"[Unknown Packet] {packet}")

    async def run(self):
        await self.connect()
        if not self.running:
            return

        asyncio.create_task(self.handle_server_messages())

        # Send example messages
        await self.send_message(packet_types.EPacketOpcode.CLIENT_MESSAGE, "Hello from MMOClient!", request_id=1)
        await asyncio.sleep(2)
        await self.send_message(packet_types.EPacketOpcode.ADD_FRIEND, "Friend: Iris", request_id=2)

        while self.running:
            await asyncio.sleep(0.1)


def signal_handler(sig, frame):
    print("Interrupt received, exiting...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    client = MMOClient()
    asyncio.run(client.run())