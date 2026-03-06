import struct

def build_packet(packet_id: int, payload: str | bytes) -> bytes:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    body = struct.pack("!H", packet_id) + payload
    return struct.pack("!I", len(body)) + body

def parse_packet(body: bytes) -> tuple[int, bytes]:
    packet_id = struct.unpack("!H", body[:2])[0]
    payload = body[2:]
    return packet_id, payload