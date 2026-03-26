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
