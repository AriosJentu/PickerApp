from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.lobby.enums import LobbyStatus
from app.modules.lobby.lobby.schemas import LobbyCreate, LobbyUpdate

from app.modules.lobby.lobby.crud import LobbyCRUD


async def get_lobby_by_id(db: AsyncSession, lobby_id: int) -> Optional[Lobby]:
    crud = LobbyCRUD(db)
    return await crud.get_by_id(lobby_id)


async def create_lobby(db: AsyncSession, lobby: LobbyCreate) -> Lobby:
    crud = LobbyCRUD(db)
    new_lobby = Lobby.from_create(lobby)
    return await crud.create(new_lobby)


async def update_lobby(db: AsyncSession, lobby: Lobby, update_data: LobbyUpdate) -> Optional[Lobby]:
    crud = LobbyCRUD(db)
    return await crud.update(lobby, update_data)


async def close_lobby(db: AsyncSession, lobby: Lobby) -> Lobby:
    return await update_lobby(db, lobby, LobbyUpdate(status=LobbyStatus.ARCHIVED))


async def delete_lobby(db: AsyncSession, lobby: Lobby) -> bool:
    crud = LobbyCRUD(db)
    return await crud.delete(lobby)


async def get_list_of_lobbies(
    db: AsyncSession, 
    id: Optional[int] = None,
    name: Optional[str] = None,
    host_id: Optional[int] = None,
    algorithm_id: Optional[int] = None,
    status: Optional[LobbyStatus] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    only_active: Optional[bool] = True,
    only_count: Optional[bool] = False
) -> list[Optional[Lobby]] | int:
    
    crud = LobbyCRUD(db)
    filters = {"id": id, "name": name, "host_id": host_id, "algorithm_id": algorithm_id, "status": status, "only_active": only_active}
    return await crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
