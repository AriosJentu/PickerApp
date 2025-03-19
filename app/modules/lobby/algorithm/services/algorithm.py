from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.lobby.algorithm.crud import AlgorithmCRUD
from app.modules.lobby.algorithm.models import Algorithm

from app.shared.service import BaseService


class AlgorithmService(BaseService[Algorithm, AlgorithmCRUD]):

    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        super().__init__(Algorithm, AlgorithmCRUD, db)
