from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.models import User

from app.modules.lobby.algorithm.schemas import (
    AlgorithmCreate, 
    AlgorithmRead,
    AlgorithmUpdate,
    AlgorithmResponse, 
    AlgorithmsListCountResponse,
)

from app.dependencies.database import get_async_session

from app.modules.lobby.algorithm.service import (
    get_algorithm_by_id,
    create_algorithm,
    update_algorithm,
    delete_algorithm,
    get_list_of_algorithms,
)

from app.modules.lobby.lobby.exceptions import (
    HTTPLobbyInternalError,
    HTTPLobbyAlgorithmNotFound,
    HTTPLobbyAlgorithmAccessDenied,
    HTTPAlgorithmCreatingFailed,
    HTTPLobbyAlgorithmUpdateDataNotProvided,
)


router = APIRouter()

@router.post("/", response_model=AlgorithmRead)
async def create_algorithm_(
    algorithm_data: AlgorithmCreate,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    algorithm = await create_algorithm(db, algorithm_data)
    if not algorithm:
        raise HTTPAlgorithmCreatingFailed()
    
    return algorithm


@router.get("/list-count", response_model=AlgorithmsListCountResponse)
async def get_count_of_algorithms_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    algorithm: Optional[str] = Query(default=None),
    teams_count: Optional[int] = Query(default=None),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    count = await get_list_of_algorithms(db, id, name, algorithm, teams_count, only_count=True)
    return AlgorithmsListCountResponse(total_count=count)


@router.get("/list", response_model=list[AlgorithmRead])
async def get_algorithms_list_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    algorithm: Optional[str] = Query(default=None),
    teams_count: Optional[int] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    algorithms = await get_list_of_algorithms(db, id, name, algorithm, teams_count, sort_by, sort_order, limit, offset)
    return algorithms


@router.get("/{algorithm_id}", response_model=AlgorithmRead)
async def get_algorithm_(
    algorithm_id: int, 
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return algorithm


@router.put("/{algorithm_id}", response_model=AlgorithmRead)
async def update_algorithm_(
    algorithm_id: int,
    update_data: AlgorithmUpdate,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    condition = (algorithm.creator_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAlgorithmAccessDenied)
    
    updated_algorithm = await update_algorithm(db, algorithm, update_data)

    if not updated_algorithm:
        raise HTTPLobbyAlgorithmUpdateDataNotProvided()
    
    return updated_algorithm


@router.delete("/{algorithm_id}", response_model=AlgorithmResponse)
async def delete_algorithm_(
    algorithm_id: int,
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    condition = (algorithm.creator_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAlgorithmAccessDenied)

    result = await delete_algorithm(db, algorithm)
    if not result:
        raise HTTPLobbyInternalError("Delete algorithm error")
    
    return AlgorithmResponse(id=algorithm_id, description=f"Algorithm '{algorithm.name}' deleted successfully")
