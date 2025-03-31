from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.user.data.models import UserData
from app.modules.user.data.crud import UserDataCRUD

from app.core.base.service import BaseService


class UserDataService(BaseService[UserData, UserDataCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(UserData, UserDataCRUD, db)
