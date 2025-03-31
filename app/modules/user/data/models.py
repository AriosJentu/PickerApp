from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from app.core.base.model import Base


class UserData(Base):

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)

    first_name = Column(String(24), nullable=True)
    last_name = Column(String(64), nullable=True)
    external_id = Column(String, unique=True, nullable=True)
    
    user = relationship("User", back_populates="data", lazy="selectin")
