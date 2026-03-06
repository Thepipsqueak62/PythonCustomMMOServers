from PythonProject.WebsocketMMO.Server.WorldServiceDaemon import database
from PythonProject.WebsocketMMO.Server.common.packet_types import EPacketOpcode


def register_handlers(pm):
    @pm.register(EPacketOpcode.CLIENT_MESSAGE)
    async def handle_client_message(packet, websocket=None, **kwargs):
        request_id = packet.get("request_id")
        payload = packet.get("payload")
        await database.insert_player_message(request_id, payload)
        print(f"[Chat] Saved message: {payload}")