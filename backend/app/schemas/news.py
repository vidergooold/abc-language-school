from pydantic import BaseModel
from typing import Optional


class NewsCreate(BaseModel):
    title: str
    tag: Optional[str] = None
    body: str
        date: Optional[str] = None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    tag: Optional[str] = None
    body: Optional[str] = None
    date: Optional[str] = None


class NewsOut(BaseModel):
    id: int
    title: str
    tag: Optional[str] = None
    body: str
    date: Optional[str] = None

    class Config:
        from_attributes = True
