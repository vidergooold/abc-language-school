from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class HomeworkStatus(str, enum.Enum):
    assigned = "assigned"         # назначено
    in_progress = "in_progress"   # в процессе
    submitted = "submitted"       # сдано
    completed = "completed"       # проверено


class Homework(Base):
    """Домашнее задание"""
    __tablename__ = "homeworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    lesson_date = Column(DateTime, nullable=True)   # дата занятия, на котором задано
    due_date = Column(DateTime, nullable=False)
    status = Column(SAEnum(HomeworkStatus), nullable=False, default=HomeworkStatus.assigned)

    # Связи
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    group = relationship("Group", backref="homeworks")
    teacher = relationship("Teacher", backref="homeworks")
