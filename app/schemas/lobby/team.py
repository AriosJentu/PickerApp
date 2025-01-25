from typing import Optional

from pydantic import BaseModel

from app.schemas.lobby.lobby import LobbyRead


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    lobby_id: int


class TeamRead(TeamBase):
    id: int
    lobby: LobbyRead


class TeamUpdate(BaseModel):
    name: Optional[str] = None