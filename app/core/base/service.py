from typing import TypeVar, Generic, Optional, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel

from app.dependencies.database import get_async_session
from app.core.base.crud import BaseCRUD
from app.shared.db.base import Base

T = TypeVar("T", bound=Base)
C = TypeVar("C", bound=BaseCRUD[T])


class BaseService(Generic[T, C]):
    
    def __init__(self, model: type[T], crud_class: type[C], db: AsyncSession = Depends(get_async_session)):
        self.model = model
        self.crud = crud_class(db)


    async def get_by_id(self, obj_id: int) -> Optional[T]:
        return await self.crud.get_by_id(obj_id)
    

    async def create(self, obj: BaseModel) -> T:
        new_obj = self.model.from_create(obj)
        return await self.crud.create(new_obj)
    

    async def update(self, obj: T, update_data: BaseModel) -> Optional[T]:
        return await self.crud.update(obj, update_data)


    async def delete(self, obj: T) -> bool:
        return await self.crud.delete(obj)

    async def get_list(
        self,
        filters: Optional[dict[str, Any]] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        only_count: Optional[bool] = False
    ) -> list[Optional[T]] | int:
        
        return await self.crud.get_list(filters, sort_by, sort_order, limit, offset, only_count)
