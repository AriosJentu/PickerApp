from typing import Self

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.enums.lobby import LobbyStatus 
from app.schemas.lobby.lobby import LobbyCreate, LobbyUpdate

class Lobby(Base):

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    host_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    algorithm_id = Column(Integer, ForeignKey("algorithm.id"), nullable=False)
    status = Column(SQLAlchemyEnum(LobbyStatus), nullable=False, default=LobbyStatus.ACTIVE)

    host = relationship("User", back_populates="lobbies", lazy="selectin")
    algorithm = relationship("Algorithm", back_populates="lobbies", lazy="selectin")
    participants = relationship("LobbyParticipant", back_populates="lobby")
    teams = relationship("Team", back_populates="lobby", cascade="all, delete-orphan")


    @classmethod
    def from_create(cls, create: LobbyCreate | LobbyUpdate) -> Self:
        dump = create.model_dump()
        return cls(**dump)
