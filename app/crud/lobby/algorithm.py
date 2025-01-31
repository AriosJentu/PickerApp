from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, asc, desc

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


async def db_delete_algorithm(db: AsyncSession, algorithm: Algorithm) -> bool:
    await db.execute(delete(Algorithm).where(Algorithm.id == algorithm.id))
    await db.commit()
    return True


async def db_get_list_of_algorithms(
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
) -> list[Algorithm]:
    query = select(Algorithm)

    if id:
        query = query.where(Algorithm.id == id)

    if name:
        query = query.where(Algorithm.name.ilike(f"%{name}%"))

    if algorithm:
        query = query.where(Algorithm.name.ilike(f"%{algorithm}%"))

    if teams_count:
        query = query.where(Algorithm.teams_count == teams_count)

    if only_count:
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar()

    sort_field = getattr(Algorithm, sort_by, None)
    if sort_field:
        query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))
    
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
