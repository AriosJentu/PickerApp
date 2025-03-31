from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.modules.auth.token.services.user import UserTokenService
from app.modules.auth.user.access import RoleChecker
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.validators import UserValidator
from app.modules.auth.user.services.user import UserService
from app.modules.auth.user.services.current import CurrentUserService
from app.modules.auth.user.schemas import (
    UserReadRegular,
    UserRead,
    UserUpdate, 
    UserResponce, 
    UserListCountResponse,
)

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionNotFound,
    HTTPUserInternalError,
    HTTPUserExceptionNoDataProvided
)


router = APIRouter()

@router.get("/list-count", response_model=UserListCountResponse)
async def get_users_count_on_conditions_(
    id: Optional[int] = Query(default=None),
    role: Optional[UserRole] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    external_id: Optional[str] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    user_service: UserService = Depends(UserService)
):
    
    filters = {
        "id": id,
        "role": role,
        "username": username,
        "email": email,
        "external_id": external_id
    }
    
    count = await user_service.get_list(filters, only_count=True)
    return UserListCountResponse(total_count=count)


@router.get("/list", response_model=list[UserReadRegular])
async def get_list_of_users_on_conditions_(
    id: Optional[int] = Query(default=None),
    role: Optional[UserRole] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    external_id: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    user_service: UserService = Depends(UserService)
):
    
    filters = {
        "id": id,
        "role": role,
        "username": username,
        "email": email,
        "external_id": external_id
    }

    users = await user_service.get_list(filters, sort_by, sort_order, limit, offset)
    return users


@router.get("/", response_model=UserReadRegular)
async def get_user_by_data_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    user_service: UserService = Depends(UserService)
):
    try:
        UserValidator.ensure_user_identifier(get_user_id, get_username, get_email)
    except ValueError as e:
        raise HTTPUserExceptionNoDataProvided(detail=str(e))
    
    user = await user_service.get_by_params(get_user_id, get_username, get_email)
    if not user:
        raise HTTPUserExceptionNotFound()

    return user


@router.put("/", response_model=UserRead)
async def update_user_information_(
    user_update: UserUpdate,
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.admin),
    user_service: UserService = Depends(UserService)
):
    try:
        UserValidator.ensure_user_identifier(get_user_id, get_username, get_email)
    except ValueError as e:
        raise HTTPUserExceptionNoDataProvided(detail=str(e))

    user = await user_service.get_by_params(get_user_id, get_username, get_email)
    if not user:
        raise HTTPUserExceptionNotFound()

    updated_user = await user_service.update(user, user_update) 
    return updated_user


@router.delete("/", response_model=UserResponce)
async def delete_user_from_base_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.admin),
    user_service: UserService = Depends(UserService)
):
    try:
        UserValidator.ensure_user_identifier(get_user_id, get_username, get_email)
    except ValueError as e:
        raise HTTPUserExceptionNoDataProvided(detail=str(e))
    
    user = await user_service.get_by_params(get_user_id, get_username, get_email)
    if not user:
        raise HTTPUserExceptionNotFound()
    
    result = await user_service.delete(user)
    if not result:
        raise HTTPUserInternalError("Delete user from base error")
    
    response = user.to_dict()
    return UserResponce(
        **response,
        detail=f"User with ID {user.id} has been deleted"
    )


@router.delete("/tokens", response_model=UserResponce)
async def clear_user_tokens_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user_service: CurrentUserService = Depends(RoleChecker.admin),
    user_service: UserService = Depends(UserService),
    user_token_service: UserTokenService = Depends(UserTokenService)
):
    try:
        UserValidator.ensure_user_identifier(get_user_id, get_username, get_email)
    except ValueError as e:
        raise HTTPUserExceptionNoDataProvided(detail=str(e))
    
    user = await user_service.get_by_params(get_user_id, get_username, get_email)
    if not user:
        raise HTTPUserExceptionNotFound()
    
    await user_token_service.deactivate_old_tokens(user)

    response = user.to_dict()
    return UserResponce(
        **response,
        detail=f"Tokens for user with ID {user.id} has been deactivated"
    )
