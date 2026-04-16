from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class EducationalProgram(Base):
    """Реализуемая образовательная программа"""
    __tablename__ = "educational_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)        # напр. "Gateway B1", "Fly High 1"
    code = Column(String(100), nullable=True)         # внутренний код программы
    language = Column(String(100), nullable=False, default="Английский")
    level = Column(String(50), nullable=True)          # A1, A2, B1, B2, C1, C2
    target_group = Column(String(100), nullable=True)  # дошкольники, школьники, взрослые
    description = Column(Text, nullable=True)
    duration_months = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    lessons = relationship("Lesson", back_populates="program", lazy="select")
