from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class TeacherCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    language_level: Optional[str] = None
    experience_years: int = 0
    bio: Optional[str] = None


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    language_level: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


class TeacherOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    subject: Optional[str] = None
    language_level: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    is_active: bool
    hired_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

