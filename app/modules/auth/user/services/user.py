from typing import Callable, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.auth.password import PasswordManager
from app.modules.auth.token.services.user import UserTokenService, UserTokens
from app.modules.auth.token.services.token import TokenService
from app.modules.auth.user.crud import UserCRUD, UserExistType
from app.modules.auth.user.exceptions import HTTPUserExceptionNoDataProvided
from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserCreate, UserUpdateSecure, UserUpdate

from app.shared.service import BaseService


class UserService(BaseService[User, UserCRUD]):

    def __init__(self, 
            db: AsyncSession = Depends(get_async_session),
            token_service: TokenService = Depends(TokenService),
            user_token_service: UserTokenService = Depends(UserTokenService),
            password_hasher: Callable[[str], str] = PasswordManager.hash
    ):
        super().__init__(User, UserCRUD, db)
        self.token_service = token_service
        self.user_token_service = user_token_service
        self.password_hasher = password_hasher


    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.crud.get_by_key_value("username", username)


    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.crud.get_by_key_value("email", email)


    async def get_by_params(self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[User]:
        if user_id:
            user = await self.get_by_id(user_id)
            if user:
                return user

        if username:
            user = await self.get_by_username(username)
            if user:
                return user

        if email:
            user = await self.get_by_email(email)
            if user:
                return user

        return None


    async def is_exist(self, user: User) -> UserExistType:
        return await self.crud.is_exist(user)


    async def create(self, user: UserCreate) -> User:
        new_user = User.from_create(user, self.password_hasher)
        return await self.crud.create(new_user)


    async def update(self,
        user: User,
        update_data: UserUpdateSecure | UserUpdate,
    ) -> User:
        
        if update_data.password:
            update_data.password = self.password_hasher(update_data.password)
            
        updated_user = await self.crud.update(user, update_data)
        if not updated_user:
            raise HTTPUserExceptionNoDataProvided("No update data provided")
        
        return updated_user


    async def update_with_tokens(self,
        user: User,
        update_data: UserUpdateSecure | UserUpdate,
    ) -> UserTokens:
        
        updated_user = await self.update(user, update_data)
        return await self.user_token_service.create_tokens(updated_user)


    async def delete(self, user: User) -> bool:
        await self.user_token_service.deactivate_old_tokens(user)
        await self.token_service.drop_inactive_tokens(user)
        return await self.crud.delete(user)
