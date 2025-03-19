from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.exceptions import HTTPUserExceptionNotFound
from app.modules.auth.user.services.current import CurrentUserService
from app.modules.auth.user.services.user import UserService

from app.modules.lobby.algorithm.services.algorithm import AlgorithmService
from app.modules.lobby.lobby.enums import LobbyStatus, LobbyParticipantRole
from app.modules.lobby.lobby.services.lobby import LobbyService
from app.modules.lobby.participant.services.participant import LobbyParticipantService
from app.modules.lobby.team.services.team import TeamService

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
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    algorithm = await algorithm_service.get_by_id(lobby.algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return await lobby_service.create(lobby)


@router.get("/list-count", response_model=LobbiesListCountResponse)
async def get_lobbies_count_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    host_id: Optional[int] = Query(default=None),
    algorithm_id: Optional[int] = Query(default=None),
    status: Optional[LobbyStatus] = Query(default=None),
    only_active: Optional[bool] = Query(default=True),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    filters = {
        "id": id,
        "name": name,
        "host_id": host_id,
        "algorithm_id": algorithm_id,
        "status": status,
        "only_active": only_active
    }
    
    count = await lobby_service.get_list(filters, only_count=True)
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
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    filters = {
        "id": id,
        "name": name,
        "host_id": host_id,
        "algorithm_id": algorithm_id,
        "status": status,
        "only_active": only_active
    }

    lobbies = await lobby_service.get_list(filters, sort_by, sort_order, limit, offset)
    return lobbies


@router.get("/{lobby_id}", response_model=LobbyRead)
async def get_lobby_info_(
    lobby_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    return lobby


@router.put("/{lobby_id}", response_model=LobbyRead)
async def update_lobby_(
    lobby_id: int,
    lobby_data: LobbyUpdate,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    updated_lobby = await lobby_service.update(lobby, lobby_data)
    if not updated_lobby:
        raise HTTPLobbyUpdateDataNotProvided()

    return updated_lobby


@router.put("/{lobby_id}/close", response_model=LobbyRead)
async def close_lobby_(
    lobby_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)

    closed_lobby = await lobby_service.close(lobby)
    if not closed_lobby:
        raise HTTPLobbyUpdateDataNotProvided()

    return closed_lobby


@router.delete("/{lobby_id}", response_model=LobbyResponse)
async def delete_lobby_(
    lobby_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    result = await lobby_service.delete(lobby)
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
    all_db_participants: Optional[bool] = Query(default=False),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    filters = {
        "id": id,
        "user_id": user_id,
        "team_id": team_id,
        "lobby_id": lobby_id,
        "role": role,
        "is_active": is_active,
        "all_db_participants": all_db_participants
    }
    
    participants_count = await participant_service.get_list(filters, only_count=True)
    return LobbyParticipantsCountResponse(total_count=participants_count)


@router.get("/{lobby_id}/participants", response_model=list[LobbyParticipantRead])
async def get_lobby_participants_(
    lobby_id: int,
    id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    team_id: Optional[int] = Query(default=None),
    role: Optional[LobbyParticipantRole] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    all_db_participants: Optional[bool] = Query(default=False),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    lobby = await lobby_service.get_by_id(lobby_id)
    if not lobby:
        raise HTTPLobbyNotFound()
    
    filters = {
        "id": id,
        "user_id": user_id,
        "team_id": team_id,
        "lobby_id": lobby_id,
        "role": role,
        "is_active": is_active,
        "all_db_participants": all_db_participants
    }
    
    participants = await participant_service.get_list(filters, sort_by, sort_order, limit, offset)
    return participants


@router.post("/{lobby_id}/participants", response_model=LobbyParticipantWithLobbyRead)
async def add_participant_(
    lobby_id: int,
    user_id: int,
    team_id: Optional[int] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    user_service: UserService = Depends(UserService),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService),
    team_service: TeamService = Depends(TeamService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPUserExceptionNotFound()
    
    if team_id is not None:
        team = await team_service.get_by_id(team_id)
        if not team:
            raise HTTPTeamNotFound()
    
    if not await participant_service.is_in_lobby(lobby_id, user_id):
        return await participant_service.add(lobby_id, user_id, team_id)

    participant = await participant_service.get_by_user_id(lobby_id, user_id)
    if participant and participant.is_active:
        raise HTTPLobbyUserAlreadyIn()
    
    updated_data = LobbyParticipantUpdate(is_active=True)
    return await participant_service.update(participant, updated_data)


@router.put("/{lobby_id}/participants/{participant_id}", response_model=LobbyParticipantWithLobbyRead)
async def edit_participant_(
    lobby_id: int,
    participant_id: int,
    update_data: LobbyParticipantUpdate,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    participant = await participant_service.get_by_id(lobby_id, participant_id)
    if not participant:
        raise HTTPLobbyParticipantNotFound()
    
    updated_participant = await participant_service.update(participant, update_data)
    if not updated_participant:
        raise HTTPLobbyParticipantUpdateDataNotProvided()
    
    return updated_participant


@router.post("/{lobby_id}/connect", response_model=LobbyParticipantWithLobbyRead)
async def connect_to_lobby_(
    lobby_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()        
    
    if not await participant_service.is_in_lobby(lobby_id, current_user.id):
        return await participant_service.add(lobby_id, current_user.id)

    participant = await participant_service.get_by_user_id(lobby_id, current_user.id)
    if participant and participant.is_active:
        raise HTTPLobbyUserAlreadyIn()
    
    updated_data = LobbyParticipantUpdate(is_active=True)
    updated_participant = await participant_service.update(participant, updated_data)
    if not updated_participant:
        raise HTTPLobbyParticipantUpdateDataNotProvided()
    
    return updated_participant


@router.delete("/{lobby_id}/leave", response_model=LobbyParticipantWithLobbyRead)
async def leave_lobby_(
    lobby_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    participant = await participant_service.get_by_user_id(lobby_id, current_user.id)
    if not participant:
        raise HTTPLobbyParticipantNotFound()
    
    left_participant = await participant_service.leave(participant)
    if not left_participant:
        raise HTTPLobbyParticipantUpdateDataNotProvided()
    
    return left_participant


@router.delete("/{lobby_id}/participants/{participant_id}", response_model=LobbyParticipantWithLobbyRead)
async def kick_from_lobby_(
    lobby_id: int,
    participant_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    participant_service: LobbyParticipantService = Depends(LobbyParticipantService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAccessDenied)
    
    participant = await participant_service.get_by_id(lobby_id, participant_id)
    if not (participant and participant.is_active):
        raise HTTPLobbyParticipantNotFound()
    
    left_participant = await participant_service.leave(participant)
    if not left_participant:
        raise HTTPLobbyParticipantUpdateDataNotProvided()
    
    return left_participant
