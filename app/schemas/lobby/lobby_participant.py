from typing import Optional
from pydantic import BaseModel

from app.enums.lobby import LobbyParticipantRole

from app.schemas.auth.user import UserReadRegular
from app.schemas.lobby.lobby import LobbyRead
from app.schemas.lobby.team import TeamRead


class LobbyParticipantRead(BaseModel):
    id: int
    user: UserReadRegular
    team: Optional[TeamRead] = None
    role: LobbyParticipantRole
    is_active: bool


class LobbyParticipantWithLobbyRead(LobbyParticipantRead):
    lobby: LobbyRead


class LobbyWithParticipants(LobbyRead):
    participants: list[LobbyParticipantRead]
