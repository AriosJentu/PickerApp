from typing import Self, Callable

from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.core.base.model import Base
from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.schemas import UserCreate, UserUpdate, UserUpdateSecure


type UserScheme = UserCreate | UserUpdateSecure | UserUpdate

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
    def from_create(cls, user_create: UserScheme, password_hasher: Callable[[str], str]) -> Self:
        dump = user_create.model_dump()
        dump["password"] = password_hasher(user_create.password)
        return cls(**dump)

    
    @staticmethod
    def update_password(user_update: UserScheme, password_hasher: Callable[[str], str]) -> UserScheme:
        if user_update.password:
            user_update.password = password_hasher(user_update.password)
    
        return user_update
    