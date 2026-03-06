from AdvancedMultiServer.shared.packet_types import EPacketOpcode


def register_handlers(pm):
    @pm.register(EPacketOpcode.WORLD_EVENT)
    async def handle_world_event(packet, websocket=None, **kwargs):
        print(f"[World Event] {packet.get('payload')}")