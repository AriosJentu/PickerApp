from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models.lobby.lobby import Lobby
from app.models.lobby.lobby_participant import LobbyParticipant
from app.schemas.lobby.lobby import LobbyParticipantUpdate


async def db_create_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> LobbyParticipant:
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant



async def db_get_lobby_participant_by_key_value(db: AsyncSession, key: str, value: str | int) -> Optional[LobbyParticipant]:
    result = await db.execute(select(LobbyParticipant).filter(getattr(LobbyParticipant, key) == value))
    return result.scalars().first()


async def get_lobby_participant_by_id(db: AsyncSession, participant_id: int) -> Optional[LobbyParticipant]:
    return await db_get_lobby_participant_by_key_value(db, "id", participant_id)


async def db_update_lobby_participant(db: AsyncSession, participant: LobbyParticipant, update_data: LobbyParticipantUpdate) -> Optional[LobbyParticipant]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(LobbyParticipant).where(LobbyParticipant.id == participant.id).values(**update_dict))
    await db.commit()

    await db.refresh(participant)
    return participant


async def db_delete_lobby_participant(db: AsyncSession, participant: LobbyParticipant):
    await db.execute(delete(LobbyParticipant).where(participant.id == participant.id))
    await db.commit()


async def db_get_list_of_lobby_participants(db: AsyncSession, lobby: Lobby, all_db_participants: bool = False) -> list[LobbyParticipant]:
    query = select(LobbyParticipant)

    if not all_db_participants and lobby:
        query = query.where(LobbyParticipant.lobby_id == lobby.id)

    result = await db.execute(query)
    return result.scalars().all()
