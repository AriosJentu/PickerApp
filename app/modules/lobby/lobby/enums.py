from enum import Enum


class LobbyParticipantRole(str, Enum):
    PLAYER      = "player"
    SPECTATOR   = "spectator"


class LobbyStatus(str, Enum):
    ACTIVE      = "active"
    ARCHIVED    = "archived"
