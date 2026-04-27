from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
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
    teacher_groups = relationship("TeacherGroup", back_populates="teacher", lazy="select", cascade="all, delete-orphan")


class TeacherGroup(Base):
    """Связь преподаватель-группа (many-to-many дополнительные назначения)"""
    __tablename__ = "teacher_groups"
    __table_args__ = (UniqueConstraint("teacher_id", "group_id", name="uq_teacher_group"),)

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="teacher_groups")
    group = relationship("Group", lazy="select")
