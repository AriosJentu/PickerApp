from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.db.base import User
from app.modules.auth.user.enums import UserRole

from app.modules.auth.user.schemas import UserUpdate
from app.core.security.password import get_password_hash
from app.modules.auth.user.crud import db_create_user


class UserFactory:

    def __init__(self, db_async: AsyncSession):
        self.db_async = db_async

    async def create_from_data(self, data: dict[str, str | UserRole]) -> User:
        user_create = UserUpdate(**data)
        user = User.from_create(user_create, get_password_hash)
        return await db_create_user(self.db_async, user)
    
    async def create(self, 
            prefix: str = "defaultuser", 
            role: UserRole = UserRole.USER, 
            suffix: str = "",
            password: str = "SecurePassword1!"
    ) -> User:
        data = {
            "username": f"{prefix}{suffix}",
            "email": f"{prefix}{suffix}@example.com",
            "password": password,
            "role": role
        }

        return await self.create_from_data(data)
