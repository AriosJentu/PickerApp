from typing import Callable, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.token.services.user import UserTokenService, UserTokens
from app.modules.auth.user.crud import UserCRUD, UserExistType
from app.modules.auth.user.exceptions import HTTPUserExceptionNoDataProvided, HTTPUserExceptionIncorrectFormData
from app.modules.auth.user.models import User
from app.modules.auth.user.validators import UserValidator
from app.modules.auth.user.schemas import UserCreate, UserUpdateSecure, UserUpdate

from app.core.base.service import BaseService


class UserService(BaseService[User, UserCRUD]):

    def __init__(self, 
            db: AsyncSession = Depends(get_async_session),
            user_token_service: UserTokenService = Depends(UserTokenService)
    ):
        super().__init__(User, UserCRUD, db)
        self.user_token_service = user_token_service


    def validate_form_data(self, form_data: OAuth2PasswordRequestForm) -> None:
        try:
            UserValidator.username(form_data.username)
            UserValidator.password(form_data.password)
        except ValueError as error:
            raise HTTPUserExceptionIncorrectFormData(str(error))


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
        new_user = User.from_create(user)
        return await self.crud.create(new_user)


    async def update(self,
        user: User,
        update_data: UserUpdateSecure | UserUpdate,
    ) -> User:
        
        update_data = User.update_password(update_data)
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
        await self.user_token_service.delete_tokens(user)
        return await self.crud.delete(user)
