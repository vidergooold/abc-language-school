from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.waitlist import WaitlistStatus


class WaitlistCreate(BaseModel):
    course_id:     int
    group_id:      Optional[int] = None
    student_name:  str
    student_phone: Optional[str] = None
    student_email: Optional[EmailStr] = None
    student_type:  str = "adult"
    comment:       Optional[str] = None


class WaitlistOut(BaseModel):
    id:            int
    course_id:     int
    group_id:      Optional[int]
    student_name:  str
    student_phone: Optional[str]
    student_email: Optional[str]
    student_type:  str
    position:      int
    status:        WaitlistStatus
    comment:       Optional[str]
    notified_at:   Optional[datetime]
    enrolled_at:   Optional[datetime]
    created_at:    Optional[datetime] = None

    model_config = {"from_attributes": True}
