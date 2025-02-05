from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.user import UserRole
from app.models.auth.user import User

from app.schemas.lobby.algorithm import (
    AlgorithmCreate, 
    AlgorithmRead,
    AlgorithmUpdate,
    AlgorithmResponse, 
    AlgorithmsListCountResponse,
)

from app.db.session import get_async_session

from app.core.lobby.algorithm import (
    get_algorithm_by_id,
    create_algorithm,
    update_algorithm,
    delete_algorithm,
    get_list_of_algorithms,
)
from app.core.security.decorators import regular, process_has_access_or
from app.core.security.user import get_current_user

from app.exceptions.lobby import (
    HTTPLobbyInternalError,
    HTTPLobbyAlgorithmNotFound,
    HTTPLobbyAlgorithmAccessDenied,
    HTTPAlgorithmCreatingFailed,
)


router = APIRouter()

@router.post("/", response_model=AlgorithmRead)
@regular
async def create_algorithm_(
    algorithm_data: AlgorithmCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    algorithm = await create_algorithm(db, algorithm_data)
    if not algorithm:
        raise HTTPAlgorithmCreatingFailed()
    
    return algorithm


@router.get("/list-count", response_model=AlgorithmsListCountResponse)
@regular
async def get_count_of_algorithms_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    algorithm: Optional[str] = Query(default=None),
    teams_count: Optional[int] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    count = await get_list_of_algorithms(db, id, name, algorithm, teams_count, only_count=True)
    return AlgorithmsListCountResponse(total_count=count)


@router.get("/list", response_model=list[AlgorithmRead])
@regular
async def get_algorithms_list_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    algorithm: Optional[str] = Query(default=None),
    teams_count: Optional[int] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    algorithms = await get_list_of_algorithms(db, id, name, algorithm, teams_count, sort_by, sort_order, limit, offset)
    return algorithms


@router.get("/{algorithm_id}", response_model=AlgorithmRead)
@regular
async def get_algorithm_(
    algorithm_id: int, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return algorithm


@router.put("/{algorithm_id}", response_model=AlgorithmRead)
@regular
async def update_algorithm_(
    algorithm_id: int,
    update_data: AlgorithmUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    process_has_access_or(current_user, UserRole.MODERATOR, algorithm.creator_id == current_user.id, exception=HTTPLobbyAlgorithmAccessDenied)
    
    updated_algorithm = await update_algorithm(db, algorithm, update_data)

    if not updated_algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return updated_algorithm


@router.delete("/{algorithm_id}", response_model=AlgorithmResponse)
@regular
async def delete_algorithm_(
    algorithm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    algorithm = await get_algorithm_by_id(db, algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    process_has_access_or(current_user, UserRole.MODERATOR, algorithm.creator_id == current_user.id, exception=HTTPLobbyAlgorithmAccessDenied)

    result = await delete_algorithm(db, algorithm)
    if not result:
        raise HTTPLobbyInternalError("Delete algorithm error")
    
    return AlgorithmResponse(id=algorithm_id, description=f"Algorithm '{algorithm.name}' deleted successfully")
