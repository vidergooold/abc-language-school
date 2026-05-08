from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AttendanceStatus(str, enum.Enum):
    present = "present"       # присутствовал
    absent = "absent"         # отсутствовал
    late = "late"             # опоздал
    excused = "excused"       # уважительная причина


class Attendance(Base):
    """Посещаемость занятий"""
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # кто отметил
    status = Column(SAEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.present)
    grade = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)     # примечание (причина отсутствия и т.д.)
    marked_at = Column(DateTime, default=datetime.utcnow)
    lesson_date = Column(DateTime, nullable=False)

    # Связи
    lesson = relationship("Lesson", back_populates="attendance_records")
    student_group = relationship("StudentGroup", back_populates="attendance_records")
    teacher = relationship("Teacher", back_populates="attendance_records")
