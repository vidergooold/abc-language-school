from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional


class ChildForm(BaseModel):
    parent_name: str
    phone: str
    email: Optional[EmailStr] = None
    child_name: str
    child_age: Optional[int] = None
    comment: Optional[str] = None


class AdultForm(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    comment: Optional[str] = None


class PreschoolForm(BaseModel):
    parent_name: str
    phone: str
    email: Optional[EmailStr] = None
    child_name: str
    child_age: Optional[int] = None
    comment: Optional[str] = None


class TeacherForm(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    experience: Optional[str] = None
    comment: Optional[str] = None


class TestingForm(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    comment: Optional[str] = None


class FeedbackForm(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    message: str
