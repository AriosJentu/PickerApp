from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.enums.lobby import LobbyParticipantRole


class LobbyParticipant(Base):

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    lobby_id = Column(Integer, ForeignKey("lobby.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    role = Column(SQLAlchemyEnum(LobbyParticipantRole), nullable=False, default=LobbyParticipantRole.SPECTATOR)

    user = relationship("User", back_populates="participants")
    lobby = relationship("Lobby", back_populates="participants")
    team = relationship("Team", back_populates="participants")
