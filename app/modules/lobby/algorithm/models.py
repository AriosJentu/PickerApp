from typing import Self

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base.base import Base
from app.modules.lobby.algorithm.schemas import AlgorithmCreate, AlgorithmUpdate

class Algorithm(Base):

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    algorithm = Column(String, nullable=False)
    teams_count = Column(Integer, nullable=False, default=2)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    lobbies = relationship("Lobby", back_populates="algorithm")
    creator = relationship("User", back_populates="algorithms", lazy="selectin")


    @classmethod
    def from_create(cls, create: AlgorithmCreate | AlgorithmUpdate) -> Self:
        dump = create.model_dump()
        return cls(**dump)
