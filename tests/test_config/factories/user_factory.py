from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.crud import UserCRUD
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserUpdate


class UserFactory:

    def __init__(self, db_async: AsyncSession):
        self.crud = UserCRUD(db_async)

    async def create_from_data(self, data: dict[str, str | UserRole]) -> User:
        user_create = UserUpdate(**data)
        user = User.from_create(user_create)
        return await self.crud.create(user)
    
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
