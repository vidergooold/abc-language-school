from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    lesson_id: int
    student_group_id: int
    status: AttendanceStatus = AttendanceStatus.present
    note: Optional[str] = None
    lesson_date: datetime


class AttendanceOut(BaseModel):
    id: int
    lesson_id: int
    student_group_id: int
    teacher_id: Optional[int] = None
    status: AttendanceStatus
    note: Optional[str] = None
    lesson_date: datetime
    marked_at: datetime

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    student_group_id: int
    student_name: str
    total_lessons: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_rate: float  # процент посещаемости
