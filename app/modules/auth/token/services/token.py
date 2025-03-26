from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.user.models import User
from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.models import Token
from app.modules.auth.token.utils import TokenManager

from app.core.base.service import BaseService


class TokenService(BaseService[Token, TokenCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(Token, TokenCRUD, db)


    def get_token_from_data(self, encode_data: dict, token_str: str) -> Token:
        return Token(
            token=token_str, 
            user_id=encode_data["user_id"], 
            token_type=encode_data["token_type"],
            expires_at=encode_data["exp"], 
            is_active=True
        )
    
    
    async def create_token(self, encode_data: dict) -> Token:
        token_str = TokenManager.create_token(encode_data)
        token = self.get_token_from_data(encode_data, token_str)
        return await self.crud.create(token)
    

    async def create_access_token(self, user: User) -> Token:
        data = TokenManager.create_data(user.username, user.id)
        encode_data = TokenManager.get_encode_access_data(data)
        return await self.create_token(encode_data)


    async def create_refresh_token(self, user: User) -> Token:
        data = TokenManager.create_data(user.username, user.id)
        encode_data = TokenManager.get_encode_refresh_data(data)
        return await self.create_token(encode_data)


    async def deactivate_old_tokens(self, user: User, token_type: str = "all"):
        await self.crud.deactivate_tokens(user, token_type)


    async def drop_inactive_tokens(self, user: User) -> int:
        return await self.crud.drop_inactive_tokens(user)


    async def drop_all_inactive_tokens(self) -> int:
        return await self.crud.drop_all_inactive_tokens()
