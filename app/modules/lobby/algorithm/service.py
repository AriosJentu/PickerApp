from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.db.base import Algorithm
from app.modules.lobby.algorithm.schemas import AlgorithmCreate, AlgorithmUpdate

from app.modules.lobby.algorithm.crud import (
    db_get_algorithm_by_id,
    db_create_algorithm,
    db_update_algorithm,
    db_delete_algorithm,
    db_get_list_of_algorithms
)


async def get_algorithm_by_id(db: AsyncSession, algorithm_id: int) -> Optional[Algorithm]:
    return await db_get_algorithm_by_id(db, algorithm_id)


async def create_algorithm(db: AsyncSession, algorithm: AlgorithmCreate) -> Algorithm:
    new_algorithm = Algorithm.from_create(algorithm)
    return await db_create_algorithm(db, new_algorithm)


async def update_algorithm(db: AsyncSession, algorithm: Algorithm, update_data: AlgorithmUpdate) -> Algorithm:
    return await db_update_algorithm(db, algorithm, update_data)


async def delete_algorithm(db: AsyncSession, algorithm: Algorithm) -> bool:
    return await db_delete_algorithm(db, algorithm)


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
    return await db_get_list_of_algorithms(db, id, name, algorithm, teams_count, sort_by, sort_order, limit, offset, only_count)
