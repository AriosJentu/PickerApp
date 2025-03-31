from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.user.data.models import UserData

from app.core.base.crud import BaseCRUD
from app.shared.components.filters import FilterField


class UserDataCRUD(BaseCRUD[UserData]):

    default_filters = {
        "id": FilterField(int),
        "first_name": FilterField(str),
        "last_name": FilterField(str),
        "external_id": FilterField(str)
    }
    

    def __init__(self, db: AsyncSession):
        super().__init__(db, UserData)


    def get_by_user(self, user: User) -> UserData:
        return self.get_by_key_value("user_id", user.id)
