from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.algorithm.models import Algorithm

from app.core.base.crud import BaseCRUD
from app.shared.components.filters import FilterField


class AlgorithmCRUD(BaseCRUD[Algorithm]):

    default_filters = {
        "id": FilterField(int),
        "name": FilterField(str),
        "algorithm": FilterField(str),
        "teams_count": FilterField(int)
    }


    def __init__(self, db: AsyncSession):
        super().__init__(db, Algorithm)
