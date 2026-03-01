from pydantic import BaseModel, EmailStr


class ChildFormCreate(BaseModel):
    fio: str
    age: str | None = None
    birthdate: str | None = None
    school: str
    grade: str
    shift: str | None = None
    extended: bool = False
    parentFio: str
    parentWork: str | None = None
    phone: str
    address: str
    email: str | None = None
    studiedBefore: str | None = None
    whereHow: str | None = None
    notes: str | None = None


class AdultFormCreate(BaseModel):
    fio: str
    age: str | None = None
    birthdate: str | None = None
    work: str | None = None
    phone: str
    address: str
    email: str | None = None
    studiedBefore: str | None = None
    whereHow: str | None = None
    notes: str | None = None


class PreschoolFormCreate(BaseModel):
    fio: str
    age: str | None = None
    birthdate: str | None = None
    kindergarten: str
    group: str
    parentFio: str
    parentWork: str | None = None
    phone: str
    address: str
    email: str | None = None
    pickupTime: str | None = None
    notes: str | None = None


class TeacherFormCreate(BaseModel):
    fio: str
    birthInfo: str
    maritalStatus: str
    education: str
    workExperience: str
    languageLevel: str
    skills: str | None = None
    qualities: str | None = None
    address: str
    phone: str
    email: EmailStr


class TestingFormCreate(BaseModel):
    fio: str
    age: str
    school: str
    grade: str
    phone: str
    testLevel: str  # elementary, middle, senior


class FeedbackFormCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None
    message: str | None = None


class FormResponse(BaseModel):
    id: int

    class Config:
        from_attributes = True
