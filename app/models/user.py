from typing import Self, Callable

from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.enums.user import UserRole
from app.schemas.user import UserCreate


class User(Base):

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    
    external_id = Column(String, unique=True, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def from_create(cls, user_create: UserCreate, get_password_hash: Callable[[str], str]) -> Self:
        dump = user_create.model_dump()
        dump["password"] = get_password_hash(user_create.password)
        return cls(**dump)
