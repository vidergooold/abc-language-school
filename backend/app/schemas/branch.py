from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BranchBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    manager_name: Optional[str] = None
    manager_position: Optional[str] = None
    working_hours: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    manager_name: Optional[str] = None
    manager_position: Optional[str] = None
    working_hours: Optional[str] = None


class BranchOut(BranchBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
