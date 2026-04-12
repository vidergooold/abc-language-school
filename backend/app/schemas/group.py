from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.group import CourseLevel, CourseCategory, GroupStatus


class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "Английский"
    level: CourseLevel
    category: CourseCategory
    duration_months: int = 9
    lessons_per_week: int = 2
    price_per_month: int
    max_students: int = 8


class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    language: str
    level: CourseLevel
    category: CourseCategory
    duration_months: int
    lessons_per_week: int
    price_per_month: int
    max_students: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    name: str
    course_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class GroupOut(BaseModel):
    id: int
    name: str
    course_id: int
    status: GroupStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentGroupCreate(BaseModel):
    group_id: int
    student_name: str
    student_phone: Optional[str] = None
    student_email: Optional[str] = None
    student_type: str  # child, adult, preschool
    form_id: Optional[int] = None


class StudentGroupOut(BaseModel):
    id: int
    group_id: int
    student_name: str
    student_phone: Optional[str] = None
    student_email: Optional[str] = None
    student_type: str
    form_id: Optional[int] = None
    enrolled_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
