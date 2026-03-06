import msgpack
from .packet_types import EPacketOpcode

def pack_packet(opcode: EPacketOpcode, request_id=0, payload=None) -> bytes:
    return msgpack.packb({
        "opcode": int(opcode),
        "request_id": request_id,
        "payload": payload
    }, use_bin_type=True)

def unpack_packet(data: bytes) -> dict:
    return msgpack.unpackb(data, raw=False)