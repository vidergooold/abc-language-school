from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Branch(Base):
    """Филиал языковой школы"""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)           # напр. "Филиал на Ленина"
    address = Column(String(500), nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    lessons = relationship("Lesson", back_populates="branch", lazy="select")
