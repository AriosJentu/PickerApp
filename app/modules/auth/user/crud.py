from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.schemas import UserCreate, UserUpdateSecure, UserUpdate

from app.shared.crud import BaseCRUD
from app.shared.filters import FilterField


type UserExistType = tuple[bool, bool]
type UserTupleType = tuple[User, User]
type UserModelOrScheme = User | UserCreate | UserUpdateSecure | UserUpdate


class UserCRUD(BaseCRUD[User]):

    default_filters = {
        "id": FilterField(int),
        "role": FilterField(UserRole),
        "username": FilterField(str),
        "email": FilterField(str),
        "external_id": FilterField(str)
    }
    

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)


    async def get_by_username_email(self, user: UserModelOrScheme) -> UserTupleType:
        user_by_username = await self.get_by_key_value("username", user.username)
        user_by_email = await self.get_by_key_value("email", user.email)
        return user_by_username, user_by_email


    async def is_user_exist(self, user: UserModelOrScheme) -> UserExistType:
        user_by_username, user_by_email = await self.get_by_username_email(user)
        return user_by_username is not None, user_by_email is not None
