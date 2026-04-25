from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Teacher(Base):
    """Преподаватель школы"""
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    subject = Column(String(100), nullable=True)  # английский, немецкий и т.д.
    language_level = Column(String(50), nullable=True)  # C1, C2 и т.д.
    experience_years = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    hired_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    groups = relationship("Group", back_populates="teacher", lazy="select")
    lessons = relationship("Lesson", back_populates="teacher", lazy="select")
    attendance_records = relationship("Attendance", back_populates="teacher", lazy="select")
