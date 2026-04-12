from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class CourseLevel(str, enum.Enum):
    beginner = "beginner"
    elementary = "elementary"
    pre_intermediate = "pre_intermediate"
    intermediate = "intermediate"
    upper_intermediate = "upper_intermediate"
    advanced = "advanced"


class CourseCategory(str, enum.Enum):
    children = "children"       # дошкольники
    school = "school"           # школьники
    adults = "adults"           # взрослые
    corporate = "corporate"     # корпоративные
    exam_prep = "exam_prep"     # подготовка к экзаменам


class Course(Base):
    """Курс / направление обучения"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=False, default="Английский")
    level = Column(SAEnum(CourseLevel), nullable=False)
    category = Column(SAEnum(CourseCategory), nullable=False)
    duration_months = Column(Integer, default=9)  # длительность в месяцах
    lessons_per_week = Column(Integer, default=2)
    price_per_month = Column(Integer, nullable=False)  # цена в рублях
    max_students = Column(Integer, default=8)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    groups = relationship("Group", back_populates="course", lazy="select")


class GroupStatus(str, enum.Enum):
    recruiting = "recruiting"   # набор
    active = "active"           # активная
    finished = "finished"       # завершена
    suspended = "suspended"     # приостановлена


class Group(Base):
    """Учебная группа"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)   # напр. "Группа A1-2024"
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(SAEnum(GroupStatus), nullable=False, default=GroupStatus.recruiting)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    course = relationship("Course", back_populates="groups")
    lessons = relationship("Lesson", back_populates="group", lazy="select")
    invoices = relationship("Invoice", back_populates="group", lazy="select")
    student_groups = relationship("StudentGroup", back_populates="group", lazy="select")


class StudentGroup(Base):
    """Привязка студента (из анкет) к группе"""
    __tablename__ = "student_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_name = Column(String(255), nullable=False)
    student_phone = Column(String(50), nullable=True)
    student_email = Column(String(255), nullable=True)
    student_type = Column(String(50), nullable=False)  # child, adult, preschool
    form_id = Column(Integer, nullable=True)  # id анкеты из соответствующей таблицы
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Связи
    group = relationship("Group", back_populates="student_groups")
    payments = relationship("Payment", back_populates="student_group", lazy="select")
    attendance_records = relationship("Attendance", back_populates="student_group", lazy="select")
