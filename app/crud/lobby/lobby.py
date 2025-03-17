from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, asc, desc

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


async def db_delete_lobby(db: AsyncSession, lobby: Lobby) -> bool:
    await db.execute(delete(Lobby).where(Lobby.id == lobby.id))
    await db.commit()
    return True


async def db_get_list_of_lobbies(
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
    query = select(Lobby)

    if id:
        query = query.where(Lobby.id == id)

    if name:
        query = query.where(Lobby.name.ilike(f"%{name}%"))

    if host_id:
        query = query.where(Lobby.host_id == host_id)

    if algorithm_id:
        query = query.where(Lobby.algorithm_id == algorithm_id)

    if status:
        query = query.where(Lobby.status == status)

    if only_active:
        query = query.where(Lobby.status == LobbyStatus.ACTIVE)

    if only_count:
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()

    sort_field = getattr(Lobby, sort_by, None)
    if sort_field:
        query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))
    
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
