from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel
from app.models.schedule import DayOfWeek, LessonStatus


class ClassroomCreate(BaseModel):
    name: str
    capacity: int = 10
    floor: Optional[int] = None
    has_projector: bool = False
    has_whiteboard: bool = True


class ClassroomOut(BaseModel):
    id: int
    name: str
    capacity: int
    branch_id: Optional[int] = None
    program_id: Optional[int] = None
    floor: Optional[int] = None
    has_projector: Optional[bool] = False
    has_whiteboard: bool
    is_active: bool

    model_config = {"from_attributes": True}


class LessonCardOut(BaseModel):
    id: int
    day: str
    course: Optional[str] = None
    time: str
    teacher: Optional[str] = None
    place: Optional[str] = None
    level: Optional[str] = None
    lesson_date: Optional[datetime] = None


class LessonCreate(BaseModel):
    group_id: int
    teacher_id: int
    classroom_id: int
    branch_id: Optional[int] = None
    program_id: Optional[int] = None
    day_of_week: DayOfWeek
    time_start: time
    time_end: time
    topic: Optional[str] = None
    is_recurring: bool = True
    lesson_date: Optional[datetime] = None


class LessonManageOut(BaseModel):
    id: int
    group_id: int
    teacher_id: int
    classroom_id: int
    branch_id: Optional[int] = None
    program_id: Optional[int] = None
    day_of_week: DayOfWeek
    time_start: time
    time_end: time
    topic: Optional[str] = None
    status: LessonStatus
    is_recurring: bool
    lesson_date: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class LessonListOut(LessonManageOut):
    group_name: Optional[str] = None
    course_name: Optional[str] = None
    teacher_name: Optional[str] = None
    classroom_name: Optional[str] = None
    branch_name: Optional[str] = None
    program_name: Optional[str] = None
    level: Optional[str] = None


class ConflictError(BaseModel):
    conflict_type: str    # "group", "teacher", "classroom"
    message: str
    conflicting_lesson_id: int
