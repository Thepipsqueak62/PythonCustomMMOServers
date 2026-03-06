from AdvancedMultiServer.DaemonServices import database
from AdvancedMultiServer.shared.packet_types import EPacketOpcode


def register_handlers(packet_manager):
    """Register packet handlers for MMOClient messages"""

    @packet_manager.register(EPacketOpcode.CLIENT_MESSAGE)
    async def handle_client_message(packet, websocket=None, **kwargs):
        request_id = packet.get("request_id")
        payload = packet.get("payload")
        print(f"[Handler] CLIENT_MESSAGE: {payload}")
        await database.insert_player_message(request_id, payload)  # 🔥 await!
        print("Saved CLIENT_MESSAGE to DB")

    @packet_manager.register(EPacketOpcode.ADD_FRIEND)
    async def handle_add_friend(packet, websocket=None, **kwargs):
        request_id = packet.get("request_id")
        payload = packet.get("payload")
        print(f"[Handler] ADD_FRIEND: {payload}")
        await database.insert_player_message(request_id, payload)  # 🔥 await!
        print("Saved ADD_FRIEND to DB")