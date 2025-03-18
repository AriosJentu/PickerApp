from typing import Optional

from pydantic import BaseModel, field_validator

from app.core.lobby.validators import validate_name

from app.modules.lobby.lobby.schemas import LobbyRead


class TeamBase(BaseModel):
    name: str

    
    @field_validator("name")
    def validate_name(cls, name: str):
        return validate_name(name, "Team")


class TeamCreate(TeamBase):
    lobby_id: int


class TeamRead(TeamBase):
    id: int


class TeamListCountResponse(BaseModel):
    total_count: int


class TeamReadWithLobby(TeamRead):
    lobby: LobbyRead


class TeamUpdate(BaseModel):
    name: Optional[str] = None


    @field_validator("name", mode="before")
    def validate_name(cls, name: Optional[str]):
        return validate_name(name, "Team")
    