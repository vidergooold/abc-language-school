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
    floor: Optional[int] = None
    has_projector: bool
    has_whiteboard: bool
    is_active: bool

    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    group_id: int
    teacher_id: int
    classroom_id: int
    day_of_week: DayOfWeek
    time_start: time
    time_end: time
    topic: Optional[str] = None
    is_recurring: bool = True
    lesson_date: Optional[datetime] = None


class LessonOut(BaseModel):
    id: int
    group_id: int
    teacher_id: int
    classroom_id: int
    day_of_week: DayOfWeek
    time_start: time
    time_end: time
    topic: Optional[str] = None
    status: LessonStatus
    is_recurring: bool
    lesson_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConflictError(BaseModel):
    conflict_type: str    # "group", "teacher", "classroom"
    message: str
    conflicting_lesson_id: int
