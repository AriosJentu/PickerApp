from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.participant.crud import LobbyParticipantCRUD
from app.modules.lobby.participant.models import LobbyParticipant
from app.modules.lobby.lobby.enums import LobbyParticipantRole
from app.modules.lobby.lobby.schemas import LobbyParticipantCreate, LobbyParticipantUpdate


async def get_lobby_participant_by_id(db: AsyncSession, lobby_id: int, participant_id: int) -> Optional[LobbyParticipant]:
    crud = LobbyParticipantCRUD(db)
    return await crud.get_by_id(lobby_id, participant_id)


async def get_lobby_participant_by_user_id(db: AsyncSession, lobby_id: int, user_id: int, is_active: Optional[bool] = None) -> Optional[LobbyParticipant]:
    crud = LobbyParticipantCRUD(db)
    return await crud.get_by_user_id(lobby_id, user_id, is_active)


async def create_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> LobbyParticipant:
    crud = LobbyParticipantCRUD(db)
    return await crud.create(participant)


async def is_participant_already_in_lobby(db: AsyncSession, lobby_id: int, user_id: int) -> bool:
    participant = await get_lobby_participant_by_user_id(db, lobby_id, user_id)
    return participant is not None


async def add_lobby_participant(db: AsyncSession, lobby_id: int, user_id: int, team_id: Optional[int] = None) -> LobbyParticipant:
   
    crud = LobbyParticipantCRUD(db)
    participant_scheme = LobbyParticipantCreate(
        user_id=user_id,
        lobby_id=lobby_id,
        team_id=team_id,
        role=LobbyParticipantRole.SPECTATOR,
        is_active=True
    )
    new_participant = LobbyParticipant.from_create(participant_scheme)
    return await crud.create(new_participant)


async def leave_lobby_participant(db: AsyncSession, participant: LobbyParticipant) -> Optional[LobbyParticipant]:
    crud = LobbyParticipantCRUD(db)
    update_data = LobbyParticipantUpdate(is_active=False)
    return await crud.update(participant, update_data)


async def update_lobby_participant(db: AsyncSession, participant: LobbyParticipant, update_data: LobbyParticipantUpdate) -> Optional[LobbyParticipant]:
    crud = LobbyParticipantCRUD(db)
    return await crud.update(participant, update_data)


async def get_list_of_lobby_participants(
    db: AsyncSession, 
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    lobby_id: Optional[int] = None, 
    team_id: Optional[int] = None,
    role: Optional[LobbyParticipantRole] = None,
    is_active: Optional[bool] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    all_db_participants: Optional[bool] = False,
    only_count: Optional[bool] = False
) -> list[Optional[LobbyParticipant]] | int:
    
    crud = LobbyParticipantCRUD(db)
    filters = {"id": id, "user_id": user_id, "team_id": team_id, "lobby_id": lobby_id, "role": role, "is_active": is_active, "all_db_participants": all_db_participants}
    return await crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
