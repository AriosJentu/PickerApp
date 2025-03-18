from typing import Self, Callable

from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.modules.base import Base
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.schemas import UserCreate, UserUpdate, UserUpdateSecure


class User(Base):

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    
    external_id = Column(String, unique=True, nullable=True)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    participants = relationship("LobbyParticipant", back_populates="user", cascade="all, delete-orphan")
    lobbies = relationship("Lobby", back_populates="host", cascade="all, delete-orphan")
    algorithms = relationship("Algorithm", back_populates="creator", cascade="all, delete-orphan")

    @classmethod
    def from_create(cls, user_create: UserCreate | UserUpdate | UserUpdateSecure, get_password_hash: Callable[[str], str]) -> Self:
        dump = user_create.model_dump()
        dump["password"] = get_password_hash(user_create.password)
        return cls(**dump)
