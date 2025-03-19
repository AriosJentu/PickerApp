from typing import Callable, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.dependencies.oauth import get_oauth2_scheme

from app.core.security.token import jwt_process_username_from_payload

from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.models import Token
from app.modules.auth.user.crud import UserCRUD, UserExistType
from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserCreate, UserUpdateSecure, UserUpdate
from app.modules.auth.user.enums import UserRole

from app.modules.auth.token.service import (
    create_access_token,
    create_refresh_token,
    verify_token, 
    deactivate_old_tokens,
    drop_inactive_tokens,
)

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionNotFound,
    HTTPUserExceptionNoDataProvided,
)


type UserTokens = tuple[Token, Token]


async def get_user_by_id(db: AsyncSession, get_user_id: int) -> Optional[User]:
    crud = UserCRUD(db)
    return await crud.get_by_id(get_user_id)


async def get_user_by_username(db: AsyncSession, get_username: str) -> Optional[User]:
    crud = UserCRUD(db)
    return await crud.get_by_key_value("username", get_username)


async def get_user_by_email(db: AsyncSession, get_email: str) -> Optional[User]:
    crud = UserCRUD(db)
    return await crud.get_by_key_value("email", get_email)


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


async def get_users_last_token(db: AsyncSession, user: User, token_type: str = "access") -> Optional[Token]:
    crud = TokenCRUD(db)
    return await crud.get_users_last_token(user, token_type)


async def deactivate_old_tokens_user(db: AsyncSession, user: User, token_type: str = "all"):
    await deactivate_old_tokens(db, user, token_type)


async def create_user_tokens(db: AsyncSession, user: User) -> UserTokens:
    await deactivate_old_tokens_user(db, user)
    access_token = await create_access_token(db, user)
    refresh_token = await create_refresh_token(db, user)
    return access_token, refresh_token


async def refresh_user_tokens(db: AsyncSession, user: User, refresh_token: str) -> UserTokens:
    await deactivate_old_tokens_user(db, user, "access")
    new_access_token = await create_access_token(db, user)
    return new_access_token, refresh_token


async def get_current_user_by_token_type(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
    token_type: str = "access"
) -> User:
    
    payload = await verify_token(db, token_str, token_type)
    username = jwt_process_username_from_payload(payload)
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
    crud = UserCRUD(db)
    return await crud.is_user_exist(user)


async def create_user(
    db: AsyncSession,
    user: UserCreate,
    password_hasher: Callable[[str], str]
) -> User:
    crud = UserCRUD(db)
    new_user = User.from_create(user, password_hasher)
    return await crud.create(new_user)


async def update_user(
    db: AsyncSession, 
    user: User, 
    update_data: UserUpdateSecure | UserUpdate,
    password_hasher: Callable[[str], str],
    with_tokens: bool = True
) -> UserTokens | User:
    
    if update_data.password:
        update_data.password = password_hasher(update_data.password)
        
    crud = UserCRUD(db)
    user = await crud.update(user, update_data)
    if not user:
        raise HTTPUserExceptionNoDataProvided("No update data provided")

    if with_tokens:
        return await create_user_tokens(db, user)
    
    return user


async def delete_user(db: AsyncSession, user: User) -> bool:
    crud = UserCRUD(db)
    await deactivate_old_tokens_user(db, user)
    await drop_inactive_tokens(db, user)
    return await crud.delete(user)


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
    
    crud = UserCRUD(db)
    filters = {"id": id, "role": role, "username": username, "email": email, "external_id": external_id}
    return await crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
