from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.services.current import CurrentUserService

from app.modules.lobby.lobby.schemas import LobbyResponse
from app.modules.lobby.lobby.services.lobby import LobbyService
from app.modules.lobby.team.services.team import TeamService

from app.modules.lobby.team.schemas import (
    TeamCreate, 
    TeamUpdate, 
    TeamReadWithLobby, 
    TeamListCountResponse,
)

from app.modules.lobby.lobby.exceptions import (
    HTTPLobbyNotFound,
    HTTPLobbyTeamAccessDenied,
    HTTPLobbyInternalError,
    HTTPTeamCreatingFailed,
    HTTPTeamNotFound,
    HTTPTeamUpdateDataNotProvided,
)


router = APIRouter()

@router.post("/", response_model=TeamReadWithLobby)
async def create_team_(
    team_data: TeamCreate,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    team_service: TeamService = Depends(TeamService)
):
    
    current_user = await current_user_service.get()
    lobby = await lobby_service.get_by_id(team_data.lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    condition = (lobby.host_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyTeamAccessDenied)
    
    team = await team_service.create(team_data)
    if not team:
        raise HTTPTeamCreatingFailed()
    
    return team


@router.get("/list-count", response_model=TeamListCountResponse)
async def get_count_of_teams_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    lobby_id: Optional[int] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    team_service: TeamService = Depends(TeamService)
):
    
    lobby = None
    if lobby_id:
        lobby = await lobby_service.get_by_id(lobby_id)

        if not lobby:
            raise HTTPLobbyNotFound()
    
    filters = {
        "id": id,
        "lobby_id": lobby_id,
        "name": name
    }

    teams_count = await team_service.get_list(filters, only_count=True)
    return TeamListCountResponse(total_count=teams_count)


@router.get("/list", response_model=list[TeamReadWithLobby])
async def get_list_of_teams_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    lobby_id: Optional[int] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    team_service: TeamService = Depends(TeamService)
):
    
    lobby = None
    if lobby_id:
        lobby = await lobby_service.get_by_id(lobby_id)

        if not lobby:
            raise HTTPLobbyNotFound()
        
    filters = {
        "id": id,
        "lobby_id": lobby_id,
        "name": name
    }
    
    teams = await team_service.get_list(filters, sort_by, sort_order, limit, offset)
    return teams


@router.get("/{team_id}", response_model=TeamReadWithLobby)
async def get_team_info_(
    team_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    team_service: TeamService = Depends(TeamService)
):
    
    team = await team_service.get_by_id(team_id)
    if not team:
        raise HTTPTeamNotFound()
    
    return team


@router.put("/{team_id}", response_model=TeamReadWithLobby)
async def update_team_(
    team_id: int,
    update_data: TeamUpdate,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    team_service: TeamService = Depends(TeamService)
):
    
    current_user = await current_user_service.get()
    team = await team_service.get_by_id(team_id)
    if not team:
        raise HTTPTeamNotFound()
    
    condition = True
    if team.lobby_id:
        lobby = await lobby_service.get_by_id(team.lobby_id)
        condition = (lobby.host_id == current_user.id)

    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyTeamAccessDenied)
    
    updated_team = await team_service.update(team, update_data)
    if not updated_team:
        raise HTTPTeamUpdateDataNotProvided()
    
    return updated_team


@router.delete("/{team_id}", response_model=LobbyResponse)
async def delete_team_(
    team_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    lobby_service: LobbyService = Depends(LobbyService),
    team_service: TeamService = Depends(TeamService)
):
    
    current_user = await current_user_service.get()
    team = await team_service.get_by_id(team_id)
    if not team:
        raise HTTPTeamNotFound()
    

    condition = True
    if team.lobby_id:
        lobby = await lobby_service.get_by_id(team.lobby_id)
        condition = (lobby.host_id == current_user.id)

    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyTeamAccessDenied)
    
    result = await team_service.delete(team)
    if not result:
        raise HTTPLobbyInternalError("Delete team error")
    
    return LobbyResponse(id=team_id, description=f"Team '{team.name}' deleted successfully")
