from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import get_password_hash
from app.models.auth.user import User
from app.schemas.auth.user import (
    UserReadRegular,
    UserRead,
    UserUpdate, 
    UserResponce, 
    UserListCountResponse,
)
from app.enums.user import UserRole

from app.core.user.user import (
    get_user_by_params,
    deactivate_old_tokens_user,
    update_user,
    delete_user,
    get_list_of_users,
)
from app.core.utils.user import ensure_user_identifier
from app.core.security.access import (
    check_user_regular_role, 
    check_user_admin_role, 
)
from app.db.session import get_async_session

from app.exceptions.user import (
    HTTPUserExceptionNotFound,
    HTTPUserInternalError
)


router = APIRouter()

@router.get("/list-count", response_model=UserListCountResponse)

async def get_users_count_on_conditions_(
    id: Optional[int] = Query(default=None),
    role: Optional[UserRole] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    external_id: Optional[str] = Query(default=None),
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session)
):
    count = await get_list_of_users(db, id, role, username, email, external_id, only_count=True)
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
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session)
):
    users = await get_list_of_users(db, id, role, username, email, external_id, sort_by, sort_order, limit, offset)
    return users


@router.get("/", response_model=UserReadRegular)
async def get_user_by_data_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(get_user_id, get_username, get_email)
    user = await get_user_by_params(db, get_user_id=get_user_id, get_username=get_username, get_email=get_email)

    if not user:
        raise HTTPUserExceptionNotFound()

    return user


@router.put("/", response_model=UserRead)
async def update_user_information_(
    user_update: UserUpdate,
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user: User = Depends(check_user_admin_role),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(get_user_id, get_username, get_email)
    user = await get_user_by_params(db, get_user_id=get_user_id, get_username=get_username, get_email=get_email)

    if not user:
        raise HTTPUserExceptionNotFound()

    updated_user = await update_user(db, user, user_update, get_password_hash, False)
    return updated_user


@router.delete("/", response_model=UserResponce)
async def delete_user_from_base_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user: User = Depends(check_user_admin_role),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(get_user_id, get_username, get_email)
    user = await get_user_by_params(db, get_user_id=get_user_id, get_username=get_username, get_email=get_email)

    if not user:
        raise HTTPUserExceptionNotFound()
    
    result = await delete_user(db, user)
    if not result:
        raise HTTPUserInternalError("Delete user from base error")
    
    response = user.to_dict()
    response["role"] = str(user.role)
    return UserResponce(
        **response,
        detail=f"User with ID {user.id} has been deleted"
    )


@router.delete("/tokens", response_model=UserResponce)
async def clear_user_tokens_(
    get_user_id: Optional[int] = Query(default=None),
    get_username: Optional[str] = Query(default=None),
    get_email: Optional[str] = Query(default=None),
    current_user: User = Depends(check_user_admin_role),
    db: AsyncSession = Depends(get_async_session)
):
    ensure_user_identifier(get_user_id, get_username, get_email)
    user = await get_user_by_params(db, get_user_id=get_user_id, get_username=get_username, get_email=get_email)

    if not user:
        raise HTTPUserExceptionNotFound()
    
    await deactivate_old_tokens_user(db, user)

    response = user.to_dict()
    response["role"] = str(user.role)
    return UserResponce(
        **response,
        detail=f"Tokens for user with ID {user.id} has been deactivated"
    )
