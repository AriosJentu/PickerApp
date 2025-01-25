from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session

from app.enums.user import UserRole
from app.enums.lobby import LobbyStatus
from app.schemas.lobby.lobby import (
    LobbyCreate, 
    LobbyRead, 
    LobbyUpdate, 
    LobbyResponse,
)

from app.models.auth.user import User
from app.core.security.user import get_current_user
from app.core.security.decorators import regular

from app.core.lobby.lobby import (
    get_lobby_by_id,
    create_lobby,
    update_lobby,
    close_lobby,
    delete_lobby,
    get_list_of_lobbies,
)
from app.core.lobby.algorithm import get_algorithm_by_id

from app.exceptions.lobby import (
    HTTPLobbyAlgorithmNotFound,
    HTTPLobbyNotFound,
    HTTPLobbyAccessDenied,
)


router = APIRouter()

@router.post("/", response_model=LobbyRead)
@regular
async def create_lobby_(
    lobby: LobbyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, lobby.algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return await create_lobby(db, lobby)


@router.put("/{lobby_id}", response_model=LobbyRead)
@regular
async def update_lobby_(
    lobby_id: int,
    lobby_data: LobbyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    if lobby.host_id != current_user.id or current_user.role == UserRole.USER:
        raise HTTPLobbyAccessDenied()

    return await update_lobby(db, lobby, lobby_data)


@router.put("/close/{lobby_id}", response_model=LobbyRead)
@regular
async def update_lobby_(
    lobby_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    if lobby.host_id != current_user.id or current_user.role == UserRole.USER:
        raise HTTPLobbyAccessDenied()

    return await close_lobby(db, lobby)


@router.delete("/{lobby_id}", response_model=LobbyResponse)
@regular
async def delete_lobby_(
    lobby_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    lobby = await get_lobby_by_id(db, lobby_id)

    if not lobby:
        raise HTTPLobbyNotFound()
    
    if lobby.host_id != current_user.id or current_user.role == UserRole.USER:
        raise HTTPLobbyAccessDenied()
    
    await delete_lobby(db, lobby_id)
    return LobbyResponse(id=lobby_id, description=f"Lobby '{lobby.name}' successfully removed")


@router.get("/", response_model=list[LobbyRead])
@regular
async def get_lobbies(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    host_id: Optional[int] = Query(default=None),
    status: Optional[LobbyStatus] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get a list of lobbies with optional filters.
    """
    lobbies = await get_list_of_lobbies()
    return lobbies
