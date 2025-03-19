from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.dependencies.oauth import get_oauth2_scheme

from app.modules.auth.user.models import User
from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.models import Token
from app.modules.auth.token.exceptions import (
    HTTPTokenExceptionInvalid,
    HTTPTokenExceptionInvalidType,
)

from app.core.security.token import jwt_create_access_token, jwt_create_refresh_token, jwt_decode_token


def create_token_for_user(user: User, token_type: str) -> Token:
    data = {"sub": user.username, "user_id": user.id}
    if token_type == "access":
        return jwt_create_access_token(data)
    return jwt_create_refresh_token(data)


async def create_access_token(db: AsyncSession, user: User):
    crud = TokenCRUD(db)
    token = create_token_for_user(user, "access")
    return await crud.create(token)


async def create_refresh_token(db: AsyncSession, user: User):
    crud = TokenCRUD(db)
    token = create_token_for_user(user, "refresh")
    return await crud.create(token)


async def deactivate_old_tokens(db: AsyncSession, user: User, token_type: str = "all"):
    crud = TokenCRUD(db)
    await crud.deactivate_tokens(user, token_type)


async def drop_inactive_tokens(db: AsyncSession, user: User) -> int:
    crud = TokenCRUD(db)
    return await crud.drop_inactive_tokens(user)


async def drop_all_inactive_tokens(db: AsyncSession) -> int:
    crud = TokenCRUD(db)
    return await crud.drop_all_inactive_tokens()
    
    
async def verify_token(
    db: AsyncSession = Depends(get_async_session),
    token_str: str = Depends(get_oauth2_scheme()),
    token_type: str = "access"
) -> dict:
    crud = TokenCRUD(db)
    payload = jwt_decode_token(token_str)

    payload_token_type = payload.get("token_type")
    if payload_token_type != token_type:
        raise HTTPTokenExceptionInvalidType()
    
    if not await crud.is_token_exist(token_str):
        raise HTTPTokenExceptionInvalid()
    
    return payload
