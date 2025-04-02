from typing import Optional

from pydantic import BaseModel, field_validator

from app.modules.auth.user.schemas import UserReadRegular
from app.modules.lobby.algorithm.schemas import AlgorithmReadSimple
from app.modules.lobby.lobby.enums import LobbyStatus, LobbyParticipantRole
from app.modules.lobby.lobby.validators import LobbyValidator


class LobbyBase(BaseModel):
    name: str
    description: Optional[str] = None
    host_id: int
    algorithm_id: int


    @field_validator("name")
    def validate_name(cls, name: str) -> str:
        return LobbyValidator.name(name, "Lobby")


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


    @field_validator("name", mode="before")
    def validate_name(cls, name: Optional[str]) -> Optional[str]:
        return LobbyValidator.name(name, "Lobby")
    

class LobbyParticipantUpdate(BaseModel):
    role: Optional[LobbyParticipantRole] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = None


class LobbyResponse(BaseModel):
    id: int
    description: str


class LobbiesListCountResponse(BaseModel):
    total_count: int


class LobbyParticipantsCountResponse(BaseModel):
    total_count: int
