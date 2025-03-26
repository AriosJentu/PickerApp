from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.lobby.enums import LobbyStatus
from app.modules.lobby.lobby.schemas import LobbyUpdate
from app.modules.lobby.lobby.crud import LobbyCRUD

from app.core.base.service import BaseService


class LobbyService(BaseService[Lobby, LobbyCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(Lobby, LobbyCRUD, db)


    async def close(self, lobby: Lobby) -> Lobby:
        return await self.update(lobby, LobbyUpdate(status=LobbyStatus.ARCHIVED))
