from __future__ import annotations
from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    name: str
    phone: str
    comment: str | None = None


class EnrollmentResponse(EnrollmentCreate):
    id: int

    class Config:
        from_attributes = True


class EnrollmentOut(BaseModel):
    id: int
    name: str
    phone: str
    comment: str | None = None

    class Config:
        from_attributes = True
