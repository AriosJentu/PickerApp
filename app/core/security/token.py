from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import User, Token
from app.db.session import get_async_session
from app.core.config import settings
from app.core.dependencies import get_oauth2_scheme
from app.crud.crud_token import (
    db_create_token, 
    db_deactivate_tokens,
    db_drop_inactive_tokens,
    db_drop_all_inactive_tokens
)

from app.crud.crud_token import (
    db_is_token_exist,
)

from app.exceptions.token import (
    HTTPTokenExceptionInvalid, 
    HTTPTokenExceptionInvalidType,
    HTTPTokenExceptionInvalidOrExpired
)


async def create_token(db: AsyncSession, data: dict, delta: timedelta, token_type: str) -> Token:

    expire = datetime.now(timezone.utc) + delta
    
    to_encode = data.copy()
    to_encode.update({"exp": expire, "token_type": token_type})
    
    token_str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token = Token(
        token=token_str, 
        user_id=data["user_id"], 
        token_type=token_type,
        expires_at=expire, 
        is_active=True
    )

    return await db_create_token(db, token)


async def create_access_token(db: AsyncSession, data: dict) -> Token:
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return await create_token(db, data, delta, "access")


async def create_refresh_token(db: AsyncSession, data: dict) -> Token:
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return await create_token(db, data, delta, "refresh")


async def deactivate_old_tokens(db: AsyncSession, user: User, token_type: str = "all"):
    await db_deactivate_tokens(db, user, token_type)


async def drop_inactive_tokens(db: AsyncSession, user: User) -> int:
    return await db_drop_inactive_tokens(db, user)


async def drop_all_inactive_tokens(db: AsyncSession) -> int:
    return await db_drop_all_inactive_tokens(db)


def decode_token(token_str: str) -> dict:
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPTokenExceptionInvalid()
    
async def verify_token(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
    token_type: str = "access"
) -> dict:
    payload = decode_token(token_str)

    payload_token_type = payload.get("token_type")
    if payload_token_type != token_type:
        raise HTTPTokenExceptionInvalidType()
    
    if not await db_is_token_exist(db, token_str):
        raise HTTPTokenExceptionInvalidOrExpired()
    
    return payload
