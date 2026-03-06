from AdvancedMultiServer.shared.packet_types import EPacketOpcode


def register_handlers(pm):
    @pm.register(EPacketOpcode.WORLD_EVENT)
    async def handle_world_event(packet, websocket=None, **kwargs):
        print(f"[WorldServer] World Event: {packet.get('payload')}")
        # Optionally forward to connected players
        if websocket and 'connected_players' in kwargs:
            for player in kwargs['connected_players']:
                await player.send(packet['raw'])  # raw MessagePack packet