import sys
import os


from PythonProject.WebsocketMMO.Server.common import messagepack_utils
from PythonProject.WebsocketMMO.Server.common.packet_types import EPacketOpcode
from PythonProject.WebsocketMMO.WorldServer import handlers
from PythonProject.WebsocketMMO.WorldServer.common import packet_manager

# Goes up: WorldServer → WebsocketMMO
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import asyncio
import websockets
import pkgutil
import importlib



pm = packet_manager.PacketManager()
connected_players = set()
world_service_ws = None

# Auto-load handlers
for _, mod_name, _ in pkgutil.iter_modules(handlers.__path__):
    module = importlib.import_module(f"WorldServer.handlers.{mod_name}")
    if hasattr(module, "register_handlers"):
        module.register_handlers(pm)

async def connect_to_world_service():
    global world_service_ws
    async with websockets.connect("ws://localhost:9000") as ws:
        world_service_ws = ws
        print("[WorldServer] Connected to WorldServiceDaemon!")

        async for msg in ws:
            packet = messagepack_utils.unpack_packet(msg)
            print(f"[WorldServer] Global event received: {packet.get('payload')}")
            for player in connected_players:
                try:
                    await player.send(msg)
                except Exception:
                    connected_players.discard(player)

async def handle_player(websocket):
    print("Player connected:", websocket.remote_address)
    connected_players.add(websocket)

    motd_packet = messagepack_utils.pack_packet(
        EPacketOpcode.MOTD, payload="Welcome to the MMO WorldServer!"
    )
    await websocket.send(motd_packet)

    async for msg in websocket:
        packet = messagepack_utils.unpack_packet(msg)
        packet['raw'] = msg
        await pm.handle_packet(packet, websocket=websocket)

        if packet['opcode'] in {EPacketOpcode.CLIENT_MESSAGE, EPacketOpcode.ADD_FRIEND} and world_service_ws:
            await world_service_ws.send(msg)

    connected_players.remove(websocket)
    print("Player disconnected:", websocket.remote_address)

async def main():
    asyncio.create_task(connect_to_world_service())

    async with websockets.serve(handle_player, "0.0.0.0", 9100):
        print("WorldServer listening on ws://0.0.0.0:9100")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())