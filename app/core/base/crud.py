from typing import Type, TypeVar, Generic, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete, func, asc, desc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import and_

from pydantic import BaseModel

from app.shared.db.base import Base
from app.shared.components.filters import FilterField


T = TypeVar("T", bound=Base)

class BaseCRUD(Generic[T]):

    default_filters: dict[str, FilterField] = {}
    relations: list[str] = []


    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model


    async def create(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


    async def get_by_key_value(self, key: str, value: Any) -> Optional[T]:
        result = await self.db.execute(
            select(self.model)
            .filter(getattr(self.model, key) == value)
        )

        return result.scalars().first()


    async def get_by_id(self, value: int) -> Optional[T]:
        return await self.get_by_key_value("id", value)


    async def update(self, obj: T, update_data: BaseModel) -> Optional[T]:
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return None

        await self.db.execute(
            update(self.model)
            .where(self.model.id == obj.id)
            .values(**update_dict)
        )

        await self.db.commit()
        await self.db.refresh(obj)

        return obj


    async def delete(self, obj: T) -> bool:
        await self.db.execute(delete(self.model).where(self.model.id == obj.id))
        await self.db.commit()
        return True


    async def get_list(self,
        filters: Optional[dict[str, Any]] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        only_count: Optional[bool] = False,
    ) -> list[Optional[T]] | int:
        
        query = select(self.model)

        if self.relations:
            for relation in self.relations:
                query = query.options(selectinload(getattr(self.model, relation)))

        if filters is None:
            filters = {}

        for key, filter_field in self.default_filters.items():
            if key not in filters and filter_field.default is not None:
                filters[key] = filter_field.default

        conditions = []
        custom_conditions = {}

        for key, value in filters.items():
            if value is None or key not in self.default_filters:
                continue

            filter_field = self.default_filters[key]
            if filter_field.is_dependent() and filters.get(filter_field.dependency) is not None:
                continue

            if filter_field.ignore or not hasattr(self.model, key):  
                custom_conditions[key] = value
                continue 

            column = getattr(self.model, key)
            condition = filter_field.apply_filter(column, value)

            if condition is not None:
                conditions.append(condition)

        conditions.extend(self.custom_filters(custom_conditions))
        if conditions:
            query = query.where(and_(*conditions))

        if only_count:
            count_query = select(func.count()).select_from(query.subquery())
            result = await self.db.execute(count_query)
            return result.scalar()

        sort_field = getattr(self.model, sort_by, None)
        if sort_field:
            query = query.order_by(asc(sort_field) if sort_order == "asc" else desc(sort_field))

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
    

    def custom_filters(self, filters: dict[str, Any]) -> list[Any]:
        return []
