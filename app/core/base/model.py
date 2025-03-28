from typing import Self, Any

from sqlalchemy.orm import DeclarativeBase

from pydantic import BaseModel


class Base(DeclarativeBase):

    def __init_subclass__(cls, **kwargs):
    
        cls.__tablename__ = cls.__name__.lower()
        super().__init_subclass__(**kwargs)

    
    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

    @classmethod
    def from_create(cls, scheme: BaseModel) -> Self:
        dump = scheme.model_dump()
        return cls(**dump)


    def __repr__(self):
        return f"<{self.__class__.__name__}({self.to_dict()})>"
