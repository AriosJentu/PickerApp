from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.lobby.algorithm.models import Algorithm
from app.modules.lobby.algorithm.schemas import AlgorithmCreate, AlgorithmUpdate

from app.modules.lobby.algorithm.crud import AlgorithmCRUD


async def get_algorithm_by_id(db: AsyncSession, algorithm_id: int) -> Optional[Algorithm]:
    crud = AlgorithmCRUD(db)
    return await crud.get_by_id(algorithm_id)


async def create_algorithm(db: AsyncSession, algorithm: AlgorithmCreate) -> Algorithm:
    crud = AlgorithmCRUD(db)
    new_algorithm = Algorithm.from_create(algorithm)
    return await crud.create(new_algorithm)


async def update_algorithm(db: AsyncSession, algorithm: Algorithm, update_data: AlgorithmUpdate) -> Algorithm:
    crud = AlgorithmCRUD(db)
    return await crud.update(algorithm, update_data)


async def delete_algorithm(db: AsyncSession, algorithm: Algorithm) -> bool:
    crud = AlgorithmCRUD(db)
    return await crud.delete(algorithm)


async def get_list_of_algorithms(
    db: AsyncSession,
    id: Optional[int] = None, 
    name: Optional[str] = None, 
    algorithm: Optional[str] = None, 
    teams_count: Optional[int] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    only_count: Optional[bool] = False
) -> list[Optional[Algorithm]] | int:
    
    crud = AlgorithmCRUD(db)
    filters = {"id": id, "name": name, "algorithm": algorithm, "teams_count": teams_count}
    return await crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
