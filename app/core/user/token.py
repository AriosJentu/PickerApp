from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import User
from app.db.session import get_async_session
from app.core.dependencies import get_oauth2_scheme
from app.crud.auth.token import (
    db_create_token, 
    db_deactivate_tokens,
    db_drop_inactive_tokens,
    db_drop_all_inactive_tokens,
)

from app.crud.auth.token import (
    db_is_token_exist,
)

from app.exceptions.token import (
    HTTPTokenExceptionInvalidType,
    HTTPTokenExceptionInvalidOrExpired,
)

from app.core.security.token import jwt_create_access_token, jwt_create_refresh_token, jwt_decode_token


async def create_access_token(db: AsyncSession, data: dict):
    token = await jwt_create_access_token(data)
    return await db_create_token(db, token)


async def create_refresh_token(db: AsyncSession, data: dict):
    token = await jwt_create_refresh_token(data)
    return await db_create_token(db, token)


async def deactivate_old_tokens(db: AsyncSession, user: User, token_type: str = "all"):
    await db_deactivate_tokens(db, user, token_type)


async def drop_inactive_tokens(db: AsyncSession, user: User) -> int:
    return await db_drop_inactive_tokens(db, user)


async def drop_all_inactive_tokens(db: AsyncSession) -> int:
    return await db_drop_all_inactive_tokens(db)
    
    
async def verify_token(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
    token_type: str = "access"
) -> dict:
    payload = jwt_decode_token(token_str)

    payload_token_type = payload.get("token_type")
    if payload_token_type != token_type:
        raise HTTPTokenExceptionInvalidType()
    
    if not await db_is_token_exist(db, token_str):
        raise HTTPTokenExceptionInvalidOrExpired()
    
    return payload
