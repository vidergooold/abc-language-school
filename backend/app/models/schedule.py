from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
)
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
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, default=10)
    floor = Column(Integer, nullable=True)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    lessons = relationship("Lesson", back_populates="classroom", lazy="select")


class LessonStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    rescheduled = "rescheduled"


class Lesson(Base):
    """
    Конкретное занятие в расписании.
    Конфликты проверяются на уровне сервиса:
      1. группа уже занята в этот день+время
      2. преподаватель уже занят в этот день+время
      3. аудитория уже занята в этот день+время
    """
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("time_start < time_end", name="ck_lessons_time_range"),
        Index("ix_lessons_group_slot", "group_id", "day_of_week", "time_start", "time_end"),
        Index("ix_lessons_teacher_slot", "teacher_id", "day_of_week", "time_start", "time_end"),
        Index("ix_lessons_classroom_slot", "classroom_id", "day_of_week", "time_start", "time_end"),
        )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)

    # Новые FK — филиал и образовательная программа
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("educational_programs.id"), nullable=True)

    day_of_week = Column(SAEnum(DayOfWeek), nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    topic = Column(String(255), nullable=True)
    status = Column(SAEnum(LessonStatus), nullable=False, default=LessonStatus.scheduled)
    lesson_date = Column(DateTime, nullable=True)
    is_recurring = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Связи
    group = relationship("Group", back_populates="lessons")
    teacher = relationship("Teacher", back_populates="lessons")
    classroom = relationship("Classroom", back_populates="lessons")
    branch = relationship("Branch", back_populates="lessons")
    program = relationship("EducationalProgram", back_populates="lessons")
    attendance_records = relationship("Attendance", back_populates="lesson", lazy="select")
