from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Lobby
from app.enums.lobby import LobbyStatus
from app.schemas.lobby.lobby import LobbyCreate, LobbyUpdate

from app.crud.lobby.lobby import (
    db_get_lobby_by_id,
    db_create_lobby,
    db_update_lobby,
    db_delete_lobby,
    db_get_list_of_lobbies,
)


async def get_lobby_by_id(db: AsyncSession, lobby_id: int) -> Optional[Lobby]:
    return await db_get_lobby_by_id(db, lobby_id)


async def create_lobby(db: AsyncSession, lobby: LobbyCreate) -> Lobby:
    new_lobby = Lobby.from_create(lobby)
    return await db_create_lobby(db, new_lobby)


async def update_lobby(db: AsyncSession, lobby: Lobby, update_data: LobbyUpdate) -> Optional[Lobby]:
    return await db_update_lobby(db, lobby, update_data)


async def close_lobby(db: AsyncSession, lobby: Lobby) -> Lobby:
    return await update_lobby(db, lobby, LobbyUpdate(status=LobbyStatus.ARCHIVED))


async def delete_lobby(db: AsyncSession, lobby: Lobby) -> bool:
    return await db_delete_lobby(db, lobby)


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
    return await db_get_list_of_lobbies(db, id, name, host_id, algorithm_id, status, sort_by, sort_order, limit, offset, only_active, only_count)
