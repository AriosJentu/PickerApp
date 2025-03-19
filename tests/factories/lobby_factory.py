from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.lobby.algorithm.models import Algorithm
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.lobby.crud_old import db_create_lobby


class LobbyFactory:

    def __init__(self, db_async: AsyncSession):
        self.db_async = db_async

    async def create(self, host: User, algorithm: Algorithm, i: int = 1) -> Lobby:
        data = {
            "name": f"Test Lobby {i}",
            "description": f"Test Lobby {i} for API testing",
            "host_id": host.id,
            "algorithm_id": algorithm.id
        }
        lobby = Lobby(**data)
        return await db_create_lobby(self.db_async, lobby)
