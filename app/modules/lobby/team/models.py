from typing import Self

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base.base import Base
from app.modules.lobby.team.schemas import TeamCreate, TeamUpdate


class Team(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lobby_id = Column(Integer, ForeignKey("lobby.id"), nullable=False)

    lobby = relationship("Lobby", back_populates="teams", lazy="selectin")
    participants = relationship("LobbyParticipant", back_populates="team")


    @classmethod
    def from_create(cls, create: TeamCreate | TeamUpdate) -> Self:
        dump = create.model_dump()
        return cls(**dump)
