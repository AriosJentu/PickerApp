from typing import Optional

from pydantic import BaseModel

from app.enums.lobby import LobbyStatus, LobbyParticipantRole
from app.schemas.auth.user import UserReadRegular
from app.schemas.lobby.algorithm import AlgorithmReadSimple


class LobbyBase(BaseModel):
    name: str
    description: Optional[str] = None
    host_id: int
    algorithm_id: int


class LobbyParticipantBase(BaseModel):
    user_id: int
    lobby_id: Optional[int] = None
    team_id: Optional[int] = None
    role: Optional[LobbyParticipantRole] = LobbyParticipantRole.SPECTATOR
    is_active: Optional[bool] = True


class LobbyCreate(LobbyBase):
    pass


class LobbyParticipantCreate(LobbyParticipantBase):
    pass


class LobbyRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    host: UserReadRegular
    algorithm: AlgorithmReadSimple
    status: LobbyStatus


class LobbyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    host_id: Optional[int] = None
    algorithm_id: Optional[int] = None
    status: Optional[LobbyStatus] = None


class LobbyParticipantUpdate(BaseModel):
    user_id: Optional[int] = None
    role: Optional[LobbyParticipantRole] = None
    team: Optional[str] = None
    is_active: Optional[bool] = None


class LobbyResponse(BaseModel):
    id: int
    description: str


class LobbiesListCountResponse(BaseModel):
    total_count: int


class LobbyParticipantsCountResponse(BaseModel):
    total_count: int
