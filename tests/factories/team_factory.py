from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Team, Lobby
from app.crud.lobby.team import db_create_team


class TeamFactory:

    def __init__(self, db_async: AsyncSession):
        self.db_async = db_async

    async def create(self, lobby: Lobby, i: int = 1) -> Team:
        data = {
            "name": f"Test Team {i}",
            "lobby_id": lobby.id
        }
        team = Team(**data)
        return await db_create_team(self.db_async, team)
