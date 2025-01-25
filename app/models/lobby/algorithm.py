from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Algorithm(Base):

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    algorithm = Column(String, nullable=False)
    teams_count = Column(Integer, nullable=False, default=2)

    lobbies = relationship("Lobby", back_populates="algorithm", cascade="all, delete-orphan")
