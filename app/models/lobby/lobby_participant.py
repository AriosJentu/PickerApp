from typing import Self

from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.enums.lobby import LobbyParticipantRole
from app.schemas.lobby.lobby import LobbyParticipantCreate, LobbyParticipantUpdate


class LobbyParticipant(Base):

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    lobby_id = Column(Integer, ForeignKey("lobby.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    role = Column(SQLAlchemyEnum(LobbyParticipantRole), nullable=False, default=LobbyParticipantRole.SPECTATOR)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="participants", lazy="selectin")
    lobby = relationship("Lobby", back_populates="participants", lazy="selectin")
    team = relationship("Team", back_populates="participants", lazy="selectin")


    @classmethod
    def from_create(cls, participant_create: LobbyParticipantCreate | LobbyParticipantUpdate) -> Self:
        dump = participant_create.model_dump()
        return cls(**dump)
