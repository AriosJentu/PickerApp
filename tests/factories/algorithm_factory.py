from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.db.base import Algorithm, User
from app.modules.lobby.algorithm.crud import db_create_algorithm


class AlgorithmFactory:

    def __init__(self, db_async: AsyncSession):
        self.db_async = db_async

    async def create(self, creator: User, i: int = 1) -> Algorithm:
        data = {
            "name": f"Test Algorithm {i}",
            "description": "Test algorithm",
            "algorithm": "BB PP T",
            "teams_count": 2,
            "creator_id": creator.id
        }
        algorithm = Algorithm(**data)
        return await db_create_algorithm(self.db_async, algorithm)
