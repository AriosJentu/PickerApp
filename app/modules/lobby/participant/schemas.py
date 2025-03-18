from typing import Optional
from pydantic import BaseModel

from app.modules.lobby.lobby.enums import LobbyParticipantRole

from app.modules.auth.user.schemas import UserReadRegular
from app.modules.lobby.lobby.schemas import LobbyRead
from app.modules.lobby.team.schemas import TeamRead


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
