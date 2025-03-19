from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.lobby.algorithm.models import Algorithm
from app.modules.lobby.lobby.crud import LobbyCRUD
from app.modules.lobby.lobby.models import Lobby


class LobbyFactory:

    def __init__(self, db_async: AsyncSession):
        self.crud = LobbyCRUD(db_async)

    async def create(self, host: User, algorithm: Algorithm, i: int = 1) -> Lobby:
        data = {
            "name": f"Test Lobby {i}",
            "description": f"Test Lobby {i} for API testing",
            "host_id": host.id,
            "algorithm_id": algorithm.id
        }
        lobby = Lobby(**data)
        return await self.crud.create(lobby)
