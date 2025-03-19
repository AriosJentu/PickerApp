from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.team.crud import TeamCRUD
from app.modules.lobby.team.models import Team


class TeamFactory:

    def __init__(self, db_async: AsyncSession):
        self.crud = TeamCRUD(db_async)

    async def create(self, lobby: Lobby, i: int = 1) -> Team:
        data = {
            "name": f"Test Team {i}",
            "lobby_id": lobby.id
        }
        team = Team(**data)
        return await self.crud.create(team)
