from enum import StrEnum


class LobbyParticipantRole(StrEnum):
    PLAYER      = "player"
    SPECTATOR   = "spectator"


class LobbyStatus(StrEnum):
    ACTIVE      = "active"
    ARCHIVED    = "archived"
