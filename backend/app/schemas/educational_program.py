from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProgramBase(BaseModel):
    name: str
    code: Optional[str] = None
    language: str = "Английский"
    level: Optional[str] = None
    target_group: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None
    is_active: bool = True


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    level: Optional[str] = None
    target_group: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None
    is_active: Optional[bool] = None


class ProgramOut(ProgramBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
