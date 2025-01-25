from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, asc, desc

from app.enums.lobby import LobbyParticipantRole
from app.models.lobby.lobby import Lobby
from app.models.lobby.lobby_participant import LobbyParticipant
from app.schemas.lobby.lobby import LobbyParticipantUpdate


async def db_create_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> LobbyParticipant:
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


async def db_get_lobby_participant_by_key_value(db: AsyncSession, lobby: Lobby, key: str, value: str | int) -> Optional[LobbyParticipant]:
    result = await db.execute(
        select(LobbyParticipant)
        .filter(
            getattr(LobbyParticipant, key) == value,
            LobbyParticipant.lobby_id == lobby.id
        )
    )
    return result.scalars().first()


async def db_get_lobby_participant_by_id(db: AsyncSession, lobby: Lobby, participant_id: int) -> Optional[LobbyParticipant]:
    return await db_get_lobby_participant_by_key_value(db, lobby, "id", participant_id)


async def db_get_lobby_participant_by_user_id(db: AsyncSession, lobby: Lobby, user_id: int) -> Optional[LobbyParticipant]:
    result = await db.execute(
        select(LobbyParticipant)
        .filter(
            LobbyParticipant.user_id == user_id, 
            LobbyParticipant.is_active == True,
            LobbyParticipant.lobby_id == lobby.id
        )
    )
    return result.scalars().first()


async def db_update_lobby_participant(db: AsyncSession, participant: LobbyParticipant, update_data: LobbyParticipantUpdate) -> Optional[LobbyParticipant]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(LobbyParticipant).where(LobbyParticipant.id == participant.id).values(**update_dict))
    await db.commit()

    await db.refresh(participant)
    return participant


async def db_delete_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> bool:
    await db.execute(delete(LobbyParticipant).where(participant.id == participant.id))
    await db.commit()
    return True


async def db_get_list_of_lobby_participants(
    db: AsyncSession,
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    lobby: Optional[Lobby] = None,
    role: Optional[LobbyParticipantRole] = None,
    is_active: Optional[bool] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    all_db_participants: Optional[bool] = False,
    only_count: Optional[bool] = False
) -> list[LobbyParticipant]:
    query = select(LobbyParticipant)

    if id:
        query = query.where(LobbyParticipant.id == id)

    if user_id:
        query = query.where(LobbyParticipant.user_id == user_id)

    if team_id:
        query = query.where(LobbyParticipant.team_id == team_id)

    if role:
        query = query.where(LobbyParticipant.role == role)

    if is_active is not None:
        query = query.where(LobbyParticipant.is_active == is_active)

    if not all_db_participants and lobby:
        query = query.where(LobbyParticipant.lobby_id == lobby.id)

    if only_count:
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()

    sort_field = getattr(LobbyParticipant, sort_by, None)
    if sort_field:
        query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
