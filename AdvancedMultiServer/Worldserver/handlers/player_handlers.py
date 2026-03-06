from PythonProject.WebsocketMMO.Server.common.packet_types import EPacketOpcode


def register_handlers(pm):
    @pm.register(EPacketOpcode.CLIENT_MESSAGE)
    async def handle_client_message(packet, websocket=None, **kwargs):
        request_id = packet.get("request_id")
        payload = packet.get("payload")
        print(f"[WorldServer] Processed CLIENT_MESSAGE: {payload}")

    @pm.register(EPacketOpcode.ADD_FRIEND)
    async def handle_add_friend(packet, websocket=None, **kwargs):
        request_id = packet.get("request_id")
        payload = packet.get("payload")
        print(f"[WorldServer] Processed ADD_FRIEND: {payload}")