from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.lobby.lobby.models import Lobby
from app.modules.lobby.participant.models import LobbyParticipant
from app.modules.lobby.team.models import Team

from app.modules.lobby.lobby.enums import LobbyParticipantRole
from app.modules.lobby.lobby.schemas import LobbyParticipantCreate, LobbyParticipantUpdate

from app.modules.lobby.participant.crud_old import (
    db_get_lobby_participant_by_id,
    db_get_lobby_participant_by_user_id,
    db_create_lobby_participant,
    db_update_lobby_participant,
    db_get_list_of_lobby_participants
)


async def get_lobby_participant_by_id(db: AsyncSession, lobby: Lobby, participant_id: int) -> Optional[LobbyParticipant]:
    return await db_get_lobby_participant_by_id(db, lobby, participant_id)


async def get_lobby_participant_by_user(db: AsyncSession, user: User, lobby: Lobby, is_active: Optional[bool] = None) -> Optional[LobbyParticipant]:
    return await db_get_lobby_participant_by_user_id(db, lobby, user.id, is_active)


async def create_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> LobbyParticipant:
    return await db_create_lobby_participant(db, participant)


async def is_participant_already_in_lobby(db: AsyncSession, user: User, lobby: Lobby) -> bool:
    participant = await get_lobby_participant_by_user(db, user, lobby)
    return participant is not None


async def add_lobby_participant(db: AsyncSession, user: User, lobby: Lobby, team: Optional[Team] = None) -> LobbyParticipant:
   
    team_id = None
    if isinstance(team, Team):
        team_id = team.id

    participant_scheme = LobbyParticipantCreate(
        user_id=user.id,
        lobby_id=lobby.id,
        team_id=team_id,
        role=LobbyParticipantRole.SPECTATOR,
        is_active=True
    )
    participant = LobbyParticipant.from_create(participant_scheme)
    return await create_lobby_participant(db, participant)


async def leave_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> Optional[LobbyParticipant]:
    update_data = LobbyParticipantUpdate(is_active=False)
    return await db_update_lobby_participant(db, participant, update_data)


async def update_lobby_participant(db: AsyncSession, participant: LobbyParticipant, update_data: LobbyParticipantUpdate) -> Optional[LobbyParticipant]:
    return await db_update_lobby_participant(db, participant, update_data)


async def get_list_of_lobby_participants(
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
) -> list[Optional[LobbyParticipant]] | int:
    return await db_get_list_of_lobby_participants(db, id, user_id, team_id, lobby, role, is_active, sort_by, sort_order, limit, offset, all_db_participants, only_count)
