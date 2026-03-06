from enum import IntEnum

class PacketID(IntEnum):
    MOTD         = 1
    PING         = 2
    IRIS         = 3
    INVENTORY    = 4
    CHAT         = 5
    QUEST_UPDATE = 6
    PLAYER_STATS = 7
    AIDAN        = 23