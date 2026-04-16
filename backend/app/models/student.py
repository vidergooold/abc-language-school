from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class StudentType(str, enum.Enum):
    preschool = "preschool"   # дошкольник
    child = "child"           # школьник
    adult = "adult"           # взрослый


class StudentStatus(str, enum.Enum):
    active = "active"         # обучается
    inactive = "inactive"     # не обучается
    graduated = "graduated"   # выпустился
    expelled = "expelled"     # отчислен


class Student(Base):
    """База студентов языковой школы"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    student_type = Column(SAEnum(StudentType), nullable=False, default=StudentType.adult)
    status = Column(SAEnum(StudentStatus), nullable=False, default=StudentStatus.active)

    # Контактные данные
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    birthdate = Column(Date, nullable=True)

    # Для детей/дошкольников
    parent_name = Column(String(255), nullable=True)
    parent_phone = Column(String(50), nullable=True)
    school_name = Column(String(255), nullable=True)  # школа / детский сад
    grade = Column(String(50), nullable=True)          # класс / группа

    # Для взрослых
    workplace = Column(String(255), nullable=True)

    # Уровень и примечания
    language_level = Column(String(50), nullable=True)  # A1, A2, B1 ...
    notes = Column(Text, nullable=True)

    # Источник (из какой анкеты создан)
    source_form_type = Column(String(50), nullable=True)  # child, adult, preschool
    source_form_id = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
