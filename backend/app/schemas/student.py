from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from app.models.student import StudentType, StudentStatus


class StudentBase(BaseModel):
    full_name: str
    student_type: StudentType = StudentType.adult
    status: StudentStatus = StudentStatus.active
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    school_name: Optional[str] = None
    grade: Optional[str] = None
    workplace: Optional[str] = None
    language_level: Optional[str] = None
    notes: Optional[str] = None
    source_form_type: Optional[str] = None
    source_form_id: Optional[int] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    student_type: Optional[StudentType] = None
    status: Optional[StudentStatus] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    school_name: Optional[str] = None
    grade: Optional[str] = None
    workplace: Optional[str] = None
    language_level: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StudentOut(StudentBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
