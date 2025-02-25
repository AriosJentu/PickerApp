from typing import Optional

from pydantic import BaseModel, field_validator

from app.core.lobby.validators import validate_name

from app.enums.lobby import LobbyStatus, LobbyParticipantRole
from app.schemas.auth.user import UserReadRegular
from app.schemas.lobby.algorithm import AlgorithmReadSimple


class LobbyBase(BaseModel):
    name: str
    description: Optional[str] = None
    host_id: int
    algorithm_id: int


    @field_validator("name")
    def validate_name(cls, name: str):
        return validate_name(name)


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
    def validate_name(cls, name: Optional[str]):
        return validate_name(name)
    

class LobbyParticipantUpdate(BaseModel):
    role: Optional[LobbyParticipantRole] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = None


class LobbyParticipantUpdateWithUser(LobbyParticipantUpdate):
    user_id: Optional[int] = None


class LobbyResponse(BaseModel):
    id: int
    description: str


class LobbiesListCountResponse(BaseModel):
    total_count: int


class LobbyParticipantsCountResponse(BaseModel):
    total_count: int
