from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SAEnum, Time
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class DayOfWeek(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class Classroom(Base):
    """Аудитория / кабинет"""
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)   # напр. "Кабинет 1", "Зал A"
    capacity = Column(Integer, default=10)
    floor = Column(Integer, nullable=True)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Связи
    lessons = relationship("Lesson", back_populates="classroom", lazy="select")


class LessonStatus(str, enum.Enum):
    scheduled = "scheduled"   # запланировано
    completed = "completed"   # проведено
    cancelled = "cancelled"   # отменено
    rescheduled = "rescheduled"  # перенесено


class Lesson(Base):
    """
    Конкретное занятие в расписании.
    Перед созданием сервис проверяет три конфликта:
      1. группа уже занята в этот день+время
      2. преподаватель уже занят в этот день+время
      3. аудитория уже занята в этот день+время
    """
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)

    day_of_week = Column(SAEnum(DayOfWeek), nullable=False)
    time_start = Column(Time, nullable=False)   # время начала, напр. 09:00
    time_end = Column(Time, nullable=False)     # время конца, напр. 10:30
    topic = Column(String(255), nullable=True)  # тема урока
    status = Column(SAEnum(LessonStatus), nullable=False, default=LessonStatus.scheduled)
    lesson_date = Column(DateTime, nullable=True)  # конкретная дата (если разовое)
    is_recurring = Column(Boolean, default=True)   # регулярное (по расписанию)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Связи
    group = relationship("Group", back_populates="lessons")
    teacher = relationship("Teacher", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    attendance_records = relationship("Attendance", back_populates="lesson", lazy="select")
