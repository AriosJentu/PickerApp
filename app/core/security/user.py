from typing import Callable, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import User, Token
from app.db.session import get_async_session
from app.core.dependencies import get_oauth2_scheme
from app.schemas.auth.user import UserCreate, UserUpdateSecure, UserUpdate
from app.enums.user import UserRole

from app.core.security.token import (
    create_access_token,
    create_refresh_token,
    verify_token, 
    deactivate_old_tokens,
    drop_inactive_tokens,
)

from app.crud.auth.token import db_get_users_last_token
from app.crud.auth.user import (
    db_create_user, 
    db_get_user_by_key_value, 
    db_is_user_exist, 
    db_update_user, 
    db_delete_user,
    db_get_list_of_users,
    UserExistType,
)

from app.exceptions.token import HTTPTokenExceptionInvalid
from app.exceptions.user import (
    HTTPUserExceptionNotFound,
    HTTPUserExceptionNoDataProvided,
)


type UserTokens = tuple[Token, Token]
type UserIdentifier = int | str


async def get_user_by_id(db: AsyncSession, get_user_id: int) -> Optional[User]:
    return await db_get_user_by_key_value(db, "id", get_user_id)


async def get_user_by_username(db: AsyncSession, get_username: str) -> Optional[User]:
    return await db_get_user_by_key_value(db, "username", get_username)


async def get_user_by_email(db: AsyncSession, get_email: str) -> Optional[User]:
    return await db_get_user_by_key_value(db, "email", get_email)


async def get_user_by_params(
    db: AsyncSession,
    get_user_id: Optional[int] = None,
    get_username: Optional[str] = None,
    get_email: Optional[str] = None
) -> Optional[User]:
    
    if get_user_id is not None:
        user = await get_user_by_id(db, get_user_id)
        if user is not None:
            return user

    if get_username is not None:
        user = await get_user_by_username(db, get_username)
        if user is not None:
            return user

    if get_email is not None:
        user = await get_user_by_email(db, get_email)
        if user is not None:
            return user

    return None


def ensure_user_identifier(
    get_user_id: Optional[int] = None,
    get_username: Optional[str] = None,
    get_email: Optional[str] = None
):
    if not (get_user_id or get_username or get_email):
        raise HTTPUserExceptionNoDataProvided(
            detail="No data provided: 'get_user_id', 'get_username' or 'get_email'"
        )


async def get_users_last_token(db: AsyncSession, user: User, token_type: str = "active") -> Token:
    return await db_get_users_last_token(db, user, token_type)


async def deactivate_old_tokens_user(db: AsyncSession, user: User, token_type: str = "all"):
    await deactivate_old_tokens(db, user, token_type)


async def create_user_tokens(db: AsyncSession, user: User) -> UserTokens:
    await deactivate_old_tokens_user(db, user)
    access_token = await create_access_token(db, {"sub": user.username, "user_id": user.id})
    refresh_token = await create_refresh_token(db, {"sub": user.username, "user_id": user.id})
    return access_token, refresh_token


async def refresh_user_tokens(db: AsyncSession, user: User, refresh_token: str) -> UserTokens:
    await deactivate_old_tokens_user(db, user, "access")
    new_access_token = await create_access_token(db, {"sub": user.username, "user_id": user.id})
    return new_access_token, refresh_token


def process_username_from_payload(
    payload: dict
) -> str:
    
    username = payload.get("sub")
    if username is None:
        raise HTTPTokenExceptionInvalid()
    
    return username
    

async def get_current_user_by_token_type(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
    token_type: str = "access"
) -> User:
    
    payload = await verify_token(db, token_str, token_type)
    username = process_username_from_payload(payload)
    user = await get_user_by_username(db, username)
    if user is None:
        raise HTTPUserExceptionNotFound()

    return user


async def get_current_user(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
) -> User:
    return await get_current_user_by_token_type(db, token_str, "access")


async def get_current_user_refresh(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme())
) -> User:
    return await get_current_user_by_token_type(db, token_str, "refresh")


async def is_user_exist(db: AsyncSession, user: User) -> UserExistType:
    return await db_is_user_exist(db, user)    


async def create_user(
    db: AsyncSession,
    user: UserCreate,
    get_password_hash: Callable[[str], str]
) -> User:
    new_user = User.from_create(user, get_password_hash)
    return await db_create_user(db, new_user)


async def update_user(
    db: AsyncSession, 
    user: User, 
    update_data: UserUpdateSecure | UserUpdate,
    get_password_hash: Callable[[str], str],
    with_tokens: bool = True
) -> UserTokens | User:
    
    if update_data.password:
        update_data.password = get_password_hash(update_data.password)
        
    user = await db_update_user(db, user, update_data)
    if not user:
        raise HTTPUserExceptionNoDataProvided("No update data provided")

    if with_tokens:
        return await create_user_tokens(db, user)
    
    return user


async def delete_user(db: AsyncSession, user: User) -> bool:
    await deactivate_old_tokens_user(db, user)
    await drop_inactive_tokens(db, user)
    return await db_delete_user(db, user)


async def get_list_of_users(
    db: AsyncSession,
    id: Optional[int] = None,
    role: Optional[UserRole] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    external_id: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    only_count: Optional[bool] = False
) -> list[Optional[User]] | int:
    return await db_get_list_of_users(db, id, role, username, email, external_id, sort_by, sort_order, limit, offset, only_count)
