from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.user import UserRole
from app.models.auth.user import User

from app.schemas.lobby.lobby import LobbyResponse
from app.schemas.lobby.team import (
    TeamCreate, 
    TeamUpdate, 
    TeamReadWithLobby, 
    TeamListCountResponse,
)

from app.db.session import get_async_session

from app.core.lobby.lobby import get_lobby_by_id
from app.core.lobby.team import (
    get_team_by_id,
    create_team,
    update_team,
    delete_team,
    get_list_of_teams,
)
from app.core.security.access import (
    process_has_access_or, 
    check_user_regular_role,
)

from app.exceptions.lobby import (
    HTTPLobbyNotFound,
    HTTPLobbyTeamAccessDenied,
    HTTPLobbyInternalError,
    HTTPTeamCreatingFailed,
    HTTPTeamNotFound,
)


router = APIRouter()

@router.post("/", response_model=TeamReadWithLobby)
async def create_team_(
    team_data: TeamCreate,
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, team_data.lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    process_has_access_or(current_user, UserRole.MODERATOR, lobby.host_id == current_user.id, exception=HTTPLobbyTeamAccessDenied)
    
    team = await create_team(db, team_data)
    if not team:
        raise HTTPTeamCreatingFailed()
    
    return team


@router.get("/list-count", response_model=TeamListCountResponse)
async def get_count_of_teams_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    lobby_id: Optional[int] = Query(default=None),
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    
    lobby = None
    if lobby_id:
        lobby = await get_lobby_by_id(db, lobby_id)

        if not lobby:
            raise HTTPLobbyNotFound()
    
    teams_count = await get_list_of_teams(db, id, name, lobby, only_count=True)
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
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    
    lobby = None
    if lobby_id:
        lobby = await get_lobby_by_id(db, lobby_id)

        if not lobby:
            raise HTTPLobbyNotFound()
    
    teams = await get_list_of_teams(db, id, name, lobby, sort_by, sort_order, limit, offset)
    return teams


@router.get("/{team_id}", response_model=TeamReadWithLobby)
async def get_team_info_(
    team_id: int,
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPTeamNotFound()
    
    return team


@router.put("/{team_id}", response_model=TeamReadWithLobby)
async def update_team_(
    team_id: int,
    update_data: TeamUpdate,
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPTeamNotFound()
    
    updated_team = await update_team(db, team, update_data)

    if not updated_team:
        raise HTTPTeamNotFound()
    
    return updated_team


@router.delete("/{team_id}", response_model=LobbyResponse)
async def delete_team_(
    team_id: int,
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    team = await get_team_by_id(db, team_id)
    if not team:
        raise HTTPTeamNotFound()
    
    result = await delete_team(db, team)
    if not result:
        raise HTTPLobbyInternalError("Delete team error")
    
    return LobbyResponse(id=team_id, description=f"Team '{team.name}' deleted successfully")


# @router.get("/{team_id}/participants", response_model=list[LobbyParticipantRead])
# async def get_team_participants_(
#     team_id: int,
#     db: AsyncSession = Depends(get_async_session),
# ):
#     team = await get_team_participants(db, team_id)

#     if not team:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Team not found.",
#         )
    
#     return team
