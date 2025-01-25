from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Lobby, LobbyParticipant
from app.enums.lobby import LobbyParticipantRole
from app.schemas.lobby.lobby import LobbyParticipantUpdate

from app.crud.lobby.lobby_participant import (
    db_get_lobby_participant_by_id,
    db_create_lobby_participant,
    db_update_lobby_participant,
    db_delete_lobby_participant,
    db_get_list_of_lobby_participants
)


async def get_lobby_participant_by_id(db: AsyncSession, participant_id: int) -> Optional[LobbyParticipant]:
    return await db_get_lobby_participant_by_id(db, participant_id)


async def create_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> LobbyParticipant:
    return await db_create_lobby_participant(db, participant)


async def update_lobby_participant(db: AsyncSession, participant: LobbyParticipant, update_data: LobbyParticipantUpdate) -> LobbyParticipant:
    return await db_update_lobby_participant(db, participant, update_data)


async def delete_lobby_participant(db: AsyncSession, participant: LobbyParticipant):
    return await db_delete_lobby_participant(db, participant)


async def get_list_of_lobbies(
    db: AsyncSession, 
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    team_id: Optional[int] = None,
    lobby: Optional[Lobby] = None, 
    role: Optional[LobbyParticipantRole] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    all_db_participants: Optional[bool] = False
) -> list[LobbyParticipant]:
    return await db_get_list_of_lobby_participants(db, id, user_id, team_id, lobby, role, sort_by, sort_order, limit, offset, all_db_participants)
