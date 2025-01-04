from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import get_password_hash
from app.models.user import User
from app.schemas.user import (
    UserRead,
    UserUpdate, 
    UserResponce, 
    UserListCountResponse
)
from app.enums.user import UserRole

from app.core.security.user import (
    get_current_user, 
    get_user_by_params,
    deactivate_old_tokens_user,
    ensure_user_identifier,
    update_user,
    delete_user,
    get_list_of_users
)
from app.core.security.decorators import regular, administrator
from app.db.session import get_async_session

from app.exceptions.user import (
    HTTPUserExceptionNotFound
)


router = APIRouter()

@router.get("/list-count", response_model=UserListCountResponse)
@regular
async def get_users_count_on_conditions(
    id: Optional[int] = Query(default=None),
    role: Optional[UserRole] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    external_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    count = await get_list_of_users(db, id, role, username, email, external_id, only_count=True)
    return UserListCountResponse(total_count=count)


@router.get("/list", response_model=list[UserRead])
@regular
async def get_list_of_users_on_conditions(
    id: Optional[int] = Query(default=None),
    role: Optional[UserRole] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    external_id: Optional[str] = Query(default=None),
    sort_by: Optional[str] = Query(default="id"),
    sort_order: Optional[str] = Query(default="asc"),
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    offset: Optional[int] = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    users = await get_list_of_users(db, id, role, username, email, external_id, sort_by, sort_order, limit, offset)
    return users


@router.get("/", response_model=UserRead)
@regular
async def get_user_by_data(
    user_id: Optional[int] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(user_id, username, email)
    user = await get_user_by_params(db, user_id=user_id, username=username, email=email)

    if not user:
        raise HTTPUserExceptionNotFound()

    return user


@router.put("/", response_model=UserRead)
@administrator
async def update_user_information(
    user_update: UserUpdate,
    user_id: Optional[int] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(user_id, username, email)
    user = await get_user_by_params(db, user_id=user_id, username=username, email=email)

    if not user:
        raise HTTPUserExceptionNotFound()

    updated_user = await update_user(db, user, user_update, get_password_hash, False)
    return updated_user


@router.delete("/", response_model=UserResponce)
@administrator
async def delete_user_from_base(
    user_id: Optional[int] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    ensure_user_identifier(user_id, username, email)
    user = await get_user_by_params(db, user_id=user_id, username=username, email=email)

    if not user:
        raise HTTPUserExceptionNotFound()
    
    await delete_user(db, user)
    
    return UserResponce(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        detail=f"User with ID {user.id} has been deleted"
    )


@router.delete("/tokens", response_model=UserResponce)
@administrator
async def clear_user_tokens(
    user_id: Optional[int] = Query(default=None),
    username: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    ensure_user_identifier(user_id, username, email)
    user = await get_user_by_params(db, user_id=user_id, username=username, email=email)

    if not user:
        raise HTTPUserExceptionNotFound()
    
    await deactivate_old_tokens_user(db, user)

    return UserResponce(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        detail=f"Tokens for user with ID {user.id} has been deactivated"
    )
