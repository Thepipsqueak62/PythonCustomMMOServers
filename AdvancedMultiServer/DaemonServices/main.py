import sys
import os

from PythonProject.WebsocketMMO.Server.WorldServiceDaemon import events, handlers, database
from PythonProject.WebsocketMMO.Server.common import packet_manager, messagepack_utils

# Fix path: goes up WorldServiceDaemon → Server → WebsocketMMO
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import asyncio
import websockets
import pkgutil
import importlib



# Packet manager
pm = packet_manager.PacketManager()

# Connected WorldServers
connected_worldservers = set()

# Initialize GlobalEventScheduler
scheduler = events.GlobalEventScheduler(json_file="events.json")

# Auto-load all handlers
for _, mod_name, _ in pkgutil.iter_modules(handlers.__path__):
    module = importlib.import_module(f"Server.WorldServiceDaemon.handlers.{mod_name}")
    if hasattr(module, "register_handlers"):
        module.register_handlers(pm)

async def handle_connection(websocket):
    print("WorldServer connected:", websocket.remote_address)
    connected_worldservers.add(websocket)
    scheduler.add_server(websocket)

    try:
        async for msg in websocket:
            packet = messagepack_utils.unpack_packet(msg)
            await pm.handle_packet(packet, websocket=websocket)
    except websockets.ConnectionClosed:
        print(f"WorldServer disconnected: {websocket.remote_address}")
    finally:
        connected_worldservers.discard(websocket)
        scheduler.remove_server(websocket)

async def main():
    await database.init_db()
    asyncio.create_task(scheduler.start())

    async with websockets.serve(handle_connection, "0.0.0.0", 9000):
        print("WorldServiceDaemon running on ws://0.0.0.0:9000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())