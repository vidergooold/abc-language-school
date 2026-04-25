from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    lesson_id: int
    student_group_id: int
    status: AttendanceStatus = AttendanceStatus.present
    grade: Optional[int] = None
    note: Optional[str] = None
    lesson_date: datetime


class AttendanceUpsert(BaseModel):
    lesson_id: int
    student_group_id: int
    status: AttendanceStatus = AttendanceStatus.present
    grade: Optional[int] = None
    note: Optional[str] = None
    lesson_date: Optional[datetime] = None


class AttendanceOut(BaseModel):
    id: int
    lesson_id: int
    student_group_id: int
    teacher_id: Optional[int] = None
    status: AttendanceStatus
    grade: Optional[int] = None
    note: Optional[str] = None
    lesson_date: datetime
    marked_at: datetime


class AttendanceStats(BaseModel):
    student_group_id: int
    student_name: str
    total_lessons: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_rate: float  # процент посещаемости
