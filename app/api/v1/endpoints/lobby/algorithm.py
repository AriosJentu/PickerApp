from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.services.current import CurrentUserService

from app.modules.lobby.algorithm.services.algorithm import AlgorithmService
from app.modules.lobby.algorithm.schemas import (
    AlgorithmCreate, 
    AlgorithmRead,
    AlgorithmUpdate,
    AlgorithmResponse, 
    AlgorithmsListCountResponse,
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
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    algorithm = await algorithm_service.create(algorithm_data)
    if not algorithm:
        raise HTTPAlgorithmCreatingFailed()
    
    return algorithm


@router.get("/list-count", response_model=AlgorithmsListCountResponse)
async def get_count_of_algorithms_(
    id: Optional[int] = Query(default=None),
    name: Optional[str] = Query(default=None),
    algorithm: Optional[str] = Query(default=None),
    teams_count: Optional[int] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    
    filters = {
        "id": id,
        "name": name,
        "algorithm": algorithm,
        "teams_count": teams_count
    }
    
    count = await algorithm_service.get_list(filters, only_count=True)
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
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    
    filters = {
        "id": id,
        "name": name,
        "algorithm": algorithm,
        "teams_count": teams_count
    }

    algorithms = await algorithm_service.get_list(filters, sort_by, sort_order, limit, offset)
    return algorithms


@router.get("/{algorithm_id}", response_model=AlgorithmRead)
async def get_algorithm_(
    algorithm_id: int, 
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    
    algorithm = await algorithm_service.get_by_id(algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()
    
    return algorithm


@router.put("/{algorithm_id}", response_model=AlgorithmRead)
async def update_algorithm_(
    algorithm_id: int,
    update_data: AlgorithmUpdate,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    current_user = await current_user_service.get()
    algorithm = await algorithm_service.get_by_id(algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    condition = (algorithm.creator_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAlgorithmAccessDenied)
    
    updated_algorithm = await algorithm_service.update(algorithm, update_data)
    if not updated_algorithm:
        raise HTTPLobbyAlgorithmUpdateDataNotProvided()
    
    return updated_algorithm


@router.delete("/{algorithm_id}", response_model=AlgorithmResponse)
async def delete_algorithm_(
    algorithm_id: int,
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    algorithm_service: AlgorithmService = Depends(AlgorithmService)
):
    current_user = await current_user_service.get()
    algorithm = await algorithm_service.get_by_id(algorithm_id)
    if not algorithm:
        raise HTTPLobbyAlgorithmNotFound()

    condition = (algorithm.creator_id == current_user.id)
    AccessControl.has_access_or(current_user, UserRole.MODERATOR, condition, HTTPLobbyAlgorithmAccessDenied)

    result = await algorithm_service.delete(algorithm)
    if not result:
        raise HTTPLobbyInternalError("Delete algorithm error")
    
    return AlgorithmResponse(id=algorithm_id, description=f"Algorithm '{algorithm.name}' deleted successfully")
