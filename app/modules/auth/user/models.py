from typing import Self

from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.core.base.model import Base

from app.modules.user.data.models import UserData

from app.modules.auth.user.enums import UserRole
from app.modules.auth.auth.password import PasswordManager
from app.modules.auth.user.schemas import UserCreate, UserUpdate, UserUpdateSecure


type UserScheme = UserCreate | UserUpdateSecure | UserUpdate

class User(Base):

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    
    role = Column(SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    data = relationship("UserData", back_populates="user", cascade="all, delete-orphan", lazy="selectin", uselist=False, passive_deletes=True)
    
    participants = relationship("LobbyParticipant", back_populates="user", cascade="all, delete-orphan")
    lobbies = relationship("Lobby", back_populates="host", cascade="all, delete-orphan")
    algorithms = relationship("Algorithm", back_populates="creator", cascade="all, delete-orphan")

    @classmethod
    def from_create(cls, user_create: UserScheme) -> Self:
        dump = user_create.model_dump(exclude={"data"})
        dump["password"] = PasswordManager.hash(user_create.password)

        user = cls(**dump)
        if user_create.data:
            user.data = UserData.from_create(user_create.data)
        else:
            user.data = UserData()

        return user

    
    @staticmethod
    def update_password(user_update: UserScheme) -> UserScheme:
        if user_update.password:
            user_update.password = PasswordManager.hash(user_update.password)
    
        return user_update
