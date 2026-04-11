from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ChildForm(Base):
    """Анкета школьника"""
    __tablename__ = "child_forms"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    age = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    school = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    shift = Column(String, nullable=True)
    extended = Column(Boolean, default=False)
    parent_fio = Column(String, nullable=False)
    parent_work = Column(Text, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, nullable=True)
    studied_before = Column(String, nullable=True)
    where_how = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String, default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AdultForm(Base):
    """Анкета взрослого"""
    __tablename__ = "adult_forms"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    age = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    work = Column(Text, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, nullable=True)
    studied_before = Column(String, nullable=True)
    where_how = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String, default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PreschoolForm(Base):
    """Анкета дошкольника"""
    __tablename__ = "preschool_forms"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    age = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    kindergarten = Column(String, nullable=False)
    group = Column(String, nullable=False)
    parent_fio = Column(String, nullable=False)
    parent_work = Column(Text, nullable=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    email = Column(String, nullable=True)
    pickup_time = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    status = Column(String, default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TeacherForm(Base):
    """Анкета преподавателя"""
    __tablename__ = "teacher_forms"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    birth_info = Column(Text, nullable=False)
    marital_status = Column(String, nullable=False)
    education = Column(Text, nullable=False)
    work_experience = Column(Text, nullable=False)
    language_level = Column(String, nullable=False)
    skills = Column(Text, nullable=True)
    qualities = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    comment = Column(Text, nullable=True)
    status = Column(String, default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TestingForm(Base):
    """Заявка на тестирование"""
    __tablename__ = "testing_forms"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, nullable=False)
    age = Column(String, nullable=False)
    school = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    test_level = Column(String, nullable=False)  # elementary, middle, senior
    comment = Column(Text, nullable=True)
    status = Column(String, default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FeedbackForm(Base):
    """Форма обратной связи"""
    __tablename__ = "feedback_forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
