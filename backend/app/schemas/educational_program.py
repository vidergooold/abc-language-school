from datetime import datetime
from typing import Optional
from pydantic import BaseModel, computed_field
from app.schedule_rules import canonical_program_duration_minutes


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

    @computed_field  # type: ignore[misc]
    @property
    def lesson_duration_minutes(self) -> Optional[int]:
        return canonical_program_duration_minutes(self.name)

    model_config = {"from_attributes": True}
