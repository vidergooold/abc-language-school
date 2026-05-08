from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.homework import HomeworkStatus


class HomeworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    lesson_date: Optional[datetime] = None
    due_date: datetime
    status: HomeworkStatus = HomeworkStatus.assigned
    group_id: int
    teacher_id: int


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    lesson_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[HomeworkStatus] = None


class HomeworkOut(HomeworkBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
