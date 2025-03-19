from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.dependencies.oauth import get_oauth2_scheme

from app.modules.auth.token.crud import TokenCRUD
from app.modules.auth.token.exceptions import HTTPTokenExceptionInvalid, HTTPTokenExceptionExpired
from app.modules.auth.token.utils import TokenManager

from app.modules.auth.user.exceptions import HTTPUserExceptionNotFound
from app.modules.auth.user.models import User
from app.modules.auth.user.services.user import UserService


class CurrentUserService:
    def __init__(self,
            db: AsyncSession = Depends(get_async_session),
            user_service: UserService = Depends(UserService), # TODO: Try to understand, why without type it finds `correct` data (I don't think so)
            token_str: str = Depends(get_oauth2_scheme())
    ):
        self.user_service = user_service
        self.token_str = token_str
        self.crud = TokenCRUD(db)


    async def get_by_token_type(self, token_type: str = "access") -> User:
            
        try:
            username = TokenManager.get_username_from_token(self.token_str, token_type)
            user = await self.user_service.get_user_by_username(username)
            if user is None:
                raise HTTPUserExceptionNotFound()
            
            if not await self.crud.is_token_exist(self.token_str):
                raise HTTPTokenExceptionInvalid()
            
            return user

        except ValueError as e:
            error_message = e.args[0]
            if error_message == "Invalid token":
                raise HTTPTokenExceptionInvalid()
            elif error_message == "Token has expired":
                raise HTTPTokenExceptionExpired()
            elif error_message == "Missing username in token":
                raise HTTPUserExceptionNotFound()
            else:
                raise HTTPTokenExceptionInvalid()


    async def get(self) -> User:
        return await self.get_current_user_by_token_type(self.token_str, "access")


    async def get_refresh(self) -> User:
        return await self.get_current_user_by_token_type(self.token_str, "refresh")
