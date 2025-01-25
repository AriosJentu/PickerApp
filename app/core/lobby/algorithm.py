from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Algorithm
from app.schemas.lobby.algorithm import AlgorithmUpdate

from app.crud.lobby.algorithm import (
    db_get_algorithm_by_id,
    db_create_algorithm,
    db_update_algorithm,
    db_delete_algorithm,
    db_get_list_of_algorithms
)


async def get_algorithm_by_id(db: AsyncSession, algorithm_id: int) -> Optional[Algorithm]:
    return await db_get_algorithm_by_id(db, algorithm_id)


async def create_algorithm(db: AsyncSession, algorithm: Algorithm) -> Algorithm:
    return await db_create_algorithm(db, algorithm)


async def update_algorithm(db: AsyncSession, algorithm: Algorithm, update_data: AlgorithmUpdate) -> Algorithm:
    return await db_update_algorithm(db, algorithm, update_data)


async def delete_algorithm(db: AsyncSession, algorithm: Algorithm):
    return await db_delete_algorithm(db, algorithm)


async def get_list_of_algorithms(
    db: AsyncSession,
    id: Optional[int] = None, 
    name: Optional[str] = None, 
    algorithm: Optional[str] = None, 
    teams_count: Optional[int] = None,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "asc",
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
) -> list[Algorithm]:
    return await db_get_list_of_algorithms(db, id, name, algorithm, teams_count, sort_by, sort_order, limit, offset)
