class PacketManager:
    def __init__(self):
        self.handlers = {}

    def register(self, opcode):
        """Decorator to register a coroutine handler for an opcode"""
        def decorator(func):
            self.handlers[opcode] = func
            return func
        return decorator

    async def handle_packet(self, packet, **kwargs):
        opcode = packet.get("opcode")
        handler = self.handlers.get(opcode)
        if handler:
            await handler(packet, **kwargs)
        else:
            print(f"[PacketManager] No handler for opcode: {opcode}")