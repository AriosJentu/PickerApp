from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.modules.base import Base


class Token(Base):
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    token_type = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="tokens")
