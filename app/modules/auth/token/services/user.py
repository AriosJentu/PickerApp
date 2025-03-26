from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.models import Token
from app.modules.auth.token.services.token import TokenService
from app.modules.auth.user.models import User

from app.core.base.service import BaseService


type UserTokens = tuple[Token, Token]


class UserTokenService(BaseService[User, TokenCRUD]):
    
    def __init__(self,
            db: AsyncSession = Depends(get_async_session),
            token_service: TokenService = Depends(TokenService)
    ):
        super().__init__(User, TokenCRUD, db)
        self.token_service = token_service


    async def get_last_token(self, user: User, token_type: str = "access") -> Optional[Token]:
        return await self.crud.get_users_last_token(user, token_type)


    async def deactivate_old_tokens(self, user: User, token_type: str = "all"):
        await self.token_service.deactivate_old_tokens(user, token_type)


    async def create_tokens(self, user: User) -> UserTokens:
        await self.deactivate_old_tokens(user)
        access_token = await self.token_service.create_access_token(user)
        refresh_token = await self.token_service.create_refresh_token(user)
        return access_token, refresh_token


    async def refresh_tokens(self, user: User, refresh_token: str) -> UserTokens:
        await self.deactivate_old_tokens(user, "access")
        new_access_token = await self.token_service.create_access_token(user)
        return new_access_token, refresh_token


    async def delete_tokens(self, user: User):
        await self.deactivate_old_tokens(user)
        await self.token_service.drop_inactive_tokens(user)
