from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from app.enums.lobby import LobbyStatus, LobbyParticipantRole
from app.schemas.auth.user import UserRead
from app.schemas.lobby.algorithm import AlgorithmRead


class LobbyBase(BaseModel):
    name: str
    description: Optional[str] = None
    host_id: int
    algorithm_id: int


class LobbyParticipantBase(BaseModel):
    user_id: int
    role: Optional[LobbyParticipantRole] = LobbyParticipantRole.SPECTATOR
    team: Optional[str] = None


class LobbyCreate(LobbyBase):
    pass


class LobbyParticipantCreate(LobbyParticipantBase):
    pass


class LobbyRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    host: UserRead
    algorithm: AlgorithmRead
    status: LobbyStatus


class LobbyParticipantRead(BaseModel):
    id: int
    user: UserRead
    lobby: LobbyRead
    role: LobbyParticipantRole
    team: str


class LobbyWithParticipants(LobbyRead):
    participants: list[LobbyParticipantRead]


class LobbyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    host_id: Optional[int] = None
    algorithm_id: Optional[int] = None


class LobbyParticipantUpdate(BaseModel):
    user_id: Optional[int] = None
    lobby_id: Optional[int] = None
    role = Optional[LobbyParticipantRole] = LobbyParticipantRole.SPECTATOR
    team: Optional[str] = None
