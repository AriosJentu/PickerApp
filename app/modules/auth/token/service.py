from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.dependencies.oauth import get_oauth2_scheme

# from app.modules.auth.token.crud_old import (
#     db_is_token_exist,
#     db_create_token, 
#     db_deactivate_tokens,
#     db_drop_inactive_tokens,
#     db_drop_all_inactive_tokens
# )

from app.modules.auth.user.models import User
from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.exceptions import (
    HTTPTokenExceptionInvalid,
    HTTPTokenExceptionInvalidType,
)

from app.core.security.token import jwt_create_access_token, jwt_create_refresh_token, jwt_decode_token


async def create_access_token(db: AsyncSession, data: dict):
    crud = TokenCRUD(db)
    token = await jwt_create_access_token(data)
    return await crud.create(token)
    # return await db_create_token(db, token)


async def create_refresh_token(db: AsyncSession, data: dict):
    crud = TokenCRUD(db)
    token = await jwt_create_refresh_token(data)
    return await crud.create(token)
    # return await db_create_token(db, token)


async def deactivate_old_tokens(db: AsyncSession, user: User, token_type: str = "all"):
    crud = TokenCRUD(db)
    await crud.deactivate_tokens(user, token_type)
    # await db_deactivate_tokens(db, user, token_type)


async def drop_inactive_tokens(db: AsyncSession, user: User) -> int:
    crud = TokenCRUD(db)
    return await crud.drop_inactive_tokens(user.id)
    # return await db_drop_inactive_tokens(db, user)


async def drop_all_inactive_tokens(db: AsyncSession) -> int:
    crud = TokenCRUD(db)
    return await crud.drop_all_inactive_tokens()
    # return await db_drop_all_inactive_tokens(db)
    
    
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
    # if not await db_is_token_exist(db, token_str):
        raise HTTPTokenExceptionInvalid()
    
    return payload
