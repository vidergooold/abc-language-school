from typing import Optional
from pydantic import BaseModel, EmailStr


class ChildFormCreate(BaseModel):
    fio: str
    age: Optional[str] = None
    birthdate: Optional[str] = None
    school: str
    grade: str
    shift: Optional[str] = None
    extended: bool = False
    parentFio: str
    parentWork: Optional[str] = None
    phone: str
    address: str
    email: Optional[str] = None
    studiedBefore: Optional[str] = None
    whereHow: Optional[str] = None
    notes: Optional[str] = None


class AdultFormCreate(BaseModel):
    fio: str
    age: Optional[str] = None
    birthdate: Optional[str] = None
    work: Optional[str] = None
        phone: Optional[str] = None 
    address: Optional[str] = None
    email: Optional[str] = None
    studiedBefore: Optional[str] = None
    whereHow: Optional[str] = None
    notes: Optional[str] = None


class PreschoolFormCreate(BaseModel):
    fio: str
    age: Optional[str] = None
    birthdate: Optional[str] = None
    kindergarten: str
    group: str
    parentFio: str
    parentWork: Optional[str] = None
    phone: str
    address: str
    email: Optional[str] = None
    pickupTime: Optional[str] = None
    notes: Optional[str] = None


class TeacherFormCreate(BaseModel):
    fio: str
    birthInfo: str
    maritalStatus: str
    education: str
    workExperience: str
    languageLevel: str
    skills: Optional[str] = None
    qualities: Optional[str] = None
    address: str
    phone: str
    email: str


class TestingFormCreate(BaseModel):
    fio: str
    age: str
    school: str
    grade: str
    phone: str
    testLevel: str


class FeedbackFormCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    message: Optional[str] = None


class FormResponse(BaseModel):
    id: int

    class Config:
        from_attributes = True
