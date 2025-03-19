from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.user.enums import UserRole
from app.modules.lobby.lobby.enums import LobbyStatus, LobbyParticipantRole
from app.modules.lobby.lobby.schemas import (
    LobbyCreate, 
    LobbyRead, 
    LobbyUpdate, 
    LobbyResponse,
    LobbyParticipantUpdate,
    LobbiesListCountResponse,
    LobbyParticipantsCountResponse,
)
from app.modules.lobby.participant.schemas import (
    LobbyParticipantRead,
    LobbyParticipantWithLobbyRead,
)

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.exceptions import HTTPUserExceptionNotFound
from app.modules.auth.user.models import User
from app.modules.auth.user.service import get_user_by_id

from app.modules.lobby.lobby.service import (
    get_lobby_by_id,
    create_lobby,
    update_lobby,
    close_lobby,
    delete_lobby,
    get_list_of_lobbies,
)
from app.modules.lobby.participant.service import (
    get_lobby_participant_by_id,
    get_lobby_participant_by_user_id,
    update_lobby_participant,
    get_list_of_lobby_participants,
    is_participant_already_in_lobby,
    add_lobby_participant,
    leave_lobby_participant,
)
from app.modules.lobby.algorithm.service import get_algorithm_by_id
from app.modules.lobby.team.service import (
    get_team_by_id,
)

from app.modules.lobby.lobby.exceptions import (
    HTTPLobbyAlgorithmNotFound,
    HTTPLobbyNotFound,
    HTTPLobbyAccessDenied,
    HTTPLobbyInternalError,
    HTTPLobbyUserAlreadyIn,
    HTTPLobbyParticipantNotFound,
    HTTPLobbyUpdateDataNotProvided,
    HTTPLobbyParticipantUpdateDataNotProvided,
    HTTPTeamNotFound,
)


router = APIRouter()

@router.post("/", response_model=LobbyRead)
async def create_lobby_(
    lobby: LobbyCreate,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, lobby.algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return await create_lobby(db, lobby)


@router.get("/list-count", response_model=LobbiesListCountResponse)
async def get_lobbies_count_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    host_id: Optional[int] = Query(default=None),
    algorithm_id: Optional[int] = Query(default=None),
    status: Optional[LobbyStatus] = Query(default=None),
    only_active: Optional[bool] = Query(default=True),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    count = await get_list_of_lobbies(db, id, name, host_id, algorithm_id, status, only_active=only_active, only_count=True)
    return LobbiesListCountResponse(total_count=count)


@router.get("/list", response_model=list[LobbyRead])
async def get_lobbies_list_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    host_id: Optional[int] = Query(default=None),
    algorithm_id: Optional[int] = Query(default=None),
    status: Optional[LobbyStatus] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    only_active: Optional[bool] = Query(default=True),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    lobbies = await get_list_of_lobbies(db, id, name, host_id, algorithm_id, status, sort_by, sort_order, limit, offset, only_active)
    return lobbies


@router.get("/{lobby_id}", response_model=LobbyRead)
async def get_lobby_info_(
    lobby_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    return lobby


@router.put("/{lobby_id}", response_model=LobbyRead)
async def update_lobby_(
    lobby_id: int,
    lobby_data: LobbyUpdate,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    lobby = await update_lobby(db, lobby, lobby_data)
    if not lobby:
        raise HTTPLobbyUpdateDataNotProvided()

    return lobby


@router.put("/{lobby_id}/close", response_model=LobbyRead)
async def close_lobby_(
    lobby_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)

    lobby = await close_lobby(db, lobby)
    if not lobby:
        raise HTTPLobbyUpdateDataNotProvided()

    return lobby


@router.delete("/{lobby_id}", response_model=LobbyResponse)
async def delete_lobby_(
    lobby_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    result = await delete_lobby(db, lobby)
    if not result: 
        raise HTTPLobbyInternalError("Delete lobby error")
    
    return LobbyResponse(id=lobby_id, description=f"Lobby '{lobby.name}' successfully removed")


@router.get("/{lobby_id}/participants-count", response_model=LobbyParticipantsCountResponse)
async def get_lobby_participants_count_(
    lobby_id: int,
    id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    role: Optional[LobbyParticipantRole] = Query(default=None),
    is_active: Optional[bool] = Query(default=True),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    participants_count = await get_list_of_lobby_participants(db, id, user_id, lobby_id, team_id, role, is_active, only_count=True)
    return LobbyParticipantsCountResponse(total_count=participants_count)


@router.get("/{lobby_id}/participants", response_model=list[LobbyParticipantRead])
async def get_lobby_participants_(
    lobby_id: int,
    id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    role: Optional[LobbyParticipantRole] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    lobby = await get_lobby_by_id(db, lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    participants = await get_list_of_lobby_participants(db, id, user_id, lobby_id, team_id, role, is_active, sort_by, sort_order, limit, offset)
    return participants


@router.post("/{lobby_id}/participants", response_model=LobbyParticipantWithLobbyRead)
async def add_participant_(
    lobby_id: int,
    user_id: int,
    team_id: Optional[int] = Query(default=None),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPUserExceptionNotFound()
    
    if team_id is not None:
        team = await get_team_by_id(db, team_id)
        if not team:
            raise HTTPTeamNotFound()
    
    if not await is_participant_already_in_lobby(db, lobby_id, user_id):
        return await add_lobby_participant(db, lobby_id, user_id, team_id)

    participant = await get_lobby_participant_by_user_id(db, lobby_id, user_id)
    if participant and participant.is_active:
        raise HTTPLobbyUserAlreadyIn()
    
    updated_data = LobbyParticipantUpdate(is_active=True)
    return await update_lobby_participant(db, participant, updated_data)


@router.put("/{lobby_id}/participants/{participant_id}", response_model=LobbyParticipantWithLobbyRead)
async def edit_participant_(
    lobby_id: int,
    participant_id: int,
    update_data: LobbyParticipantUpdate,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    participant = await get_lobby_participant_by_id(db, lobby_id, participant_id)
    if not participant:
        raise HTTPLobbyParticipantNotFound()
    
    participant = await update_lobby_participant(db, participant, update_data)
    if not participant:
        raise HTTPLobbyParticipantUpdateDataNotProvided()
    
    return participant


@router.post("/{lobby_id}/connect", response_model=LobbyParticipantWithLobbyRead)
async def connect_to_lobby_(
    lobby_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()        
    
    if not await is_participant_already_in_lobby(db, lobby_id, current_user.id):
        return await add_lobby_participant(db, lobby_id, current_user.id)

    participant = await get_lobby_participant_by_user_id(db, lobby_id, current_user.id)
    if participant and participant.is_active:
        raise HTTPLobbyUserAlreadyIn()
    
    updated_data = LobbyParticipantUpdate(is_active=True)
    return await update_lobby_participant(db, participant, updated_data)


@router.delete("/{lobby_id}/leave", response_model=LobbyParticipantWithLobbyRead)
async def leave_lobby(
    lobby_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    participant = await get_lobby_participant_by_user_id(db, lobby_id, current_user.id, True)
    if not participant:
        raise HTTPLobbyParticipantNotFound()
    
    return await leave_lobby_participant(db, participant)


@router.delete("/{lobby_id}/participants/{participant_id}", response_model=LobbyParticipantWithLobbyRead)
async def kick_from_lobby_(
    lobby_id: int,
    participant_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    participant = await get_lobby_participant_by_id(db, lobby_id, participant_id)
    if not (participant and participant.is_active):
        raise HTTPLobbyParticipantNotFound()
    
    return await leave_lobby_participant(db, participant)
