from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import joinedload

from app.enums.lobby import LobbyStatus
from app.models.lobby.lobby import Lobby
from app.schemas.lobby.lobby import LobbyUpdate


async def db_create_lobby(db: AsyncSession, lobby: Lobby) -> Lobby:
    db.add(lobby)
    await db.commit()
    await db.refresh(lobby)
    return lobby


async def db_get_lobby_by_key_value(db: AsyncSession, key: str, value: str | int) -> Optional[Lobby]:
    result = await db.execute(
        select(Lobby)
        .filter(getattr(Lobby, key) == value)
        .options(joinedload(Lobby.host), joinedload(Lobby.algorithm))
    )
    return result.scalars().first()


async def db_get_lobby_by_id(db: AsyncSession, lobby_id: int) -> Optional[Lobby]:
    return await db_get_lobby_by_key_value(db, "id", lobby_id)


async def db_update_lobby(db: AsyncSession, lobby: Lobby, update_data: LobbyUpdate) -> Optional[Lobby]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(Lobby).where(Lobby.id == lobby.id).values(**update_dict))
    await db.commit()

    await db.refresh(lobby)
    return lobby


async def db_delete_lobby(db: AsyncSession, lobby: Lobby):
    await db.execute(delete(Lobby).where(Lobby.id == lobby.id))
    await db.commit()


async def db_get_list_of_lobbies(db: AsyncSession, only_active: bool = True) -> list[Lobby]:
    query = select(Lobby)

    if only_active:
        query = query.where(Lobby.status == LobbyStatus.ACTIVE)

    result = await db.execute(query)
    return result.scalars().all()
