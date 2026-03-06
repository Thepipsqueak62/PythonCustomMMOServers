from enum import IntEnum

class EPacketOpcode(IntEnum):
    MOTD = 1
    CLIENT_MESSAGE = 2
    SERVER_MESSAGE = 3
    WORLD_EVENT = 4
    SEND_MESSAGE = 5
    ADD_FRIEND = 6

# Opcodes forwarded to WorldServiceDaemon
OPCODES_FOR_DAEMONS = {
    EPacketOpcode.CLIENT_MESSAGE,
    EPacketOpcode.ADD_FRIEND
}