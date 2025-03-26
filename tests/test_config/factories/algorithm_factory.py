from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.user.models import User
from app.modules.lobby.algorithm.crud import AlgorithmCRUD
from app.modules.lobby.algorithm.models import Algorithm


class AlgorithmFactory:

    def __init__(self, db_async: AsyncSession):
        self.crud = AlgorithmCRUD(db_async)

    async def create(self, creator: User, i: int = 1) -> Algorithm:
        data = {
            "name": f"Test Algorithm {i}",
            "description": "Test algorithm",
            "algorithm": "BB PP T",
            "teams_count": 2,
            "creator_id": creator.id
        }
        algorithm = Algorithm(**data)
        return await self.crud.create(algorithm)
