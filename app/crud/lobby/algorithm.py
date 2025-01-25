from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models.lobby.algorithm import Algorithm
from app.schemas.lobby.algorithm import AlgorithmUpdate


async def db_create_algorithm(db: AsyncSession, algorithm: Algorithm) -> Algorithm:
    db.add(algorithm)
    await db.commit()
    await db.refresh(algorithm)
    return algorithm


async def db_get_algorithm_by_key_value(db: AsyncSession, key: str, value: str | int) -> Optional[Algorithm]:
    result = await db.execute(select(Algorithm).filter(getattr(Algorithm, key) == value))
    return result.scalars().first()


async def db_get_algorithm_by_id(db: AsyncSession, algorithm_id: int) -> Optional[Algorithm]:
    return await db_get_algorithm_by_key_value(db, "id", algorithm_id)


async def db_update_algorithm(db: AsyncSession, algorithm: Algorithm, update_data: AlgorithmUpdate) -> Optional[Algorithm]:
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return None
    
    await db.execute(update(Algorithm).where(Algorithm.id == algorithm.id).values(**update_dict))
    await db.commit()
    
    await db.refresh(algorithm)
    return algorithm


async def db_delete_algorithm(db: AsyncSession, algorithm: Algorithm):
    await db.execute(delete(Algorithm).where(Algorithm.id == algorithm.id))
    await db.commit()


async def db_get_list_of_algorithms(db: AsyncSession) -> list[Algorithm]:
    query = select(Algorithm)
    result = await db.execute(query)
    return result.scalars().all()
