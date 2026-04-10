from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.news import NewsStatus


class NewsCreate(BaseModel):
    title: str
    tag: Optional[str] = None
    body: str
    status: NewsStatus = NewsStatus.draft
    publish_at: Optional[datetime] = None  # для отложенной публикации


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    tag: Optional[str] = None
    body: Optional[str] = None
    status: Optional[NewsStatus] = None
    publish_at: Optional[datetime] = None


class NewsOut(BaseModel):
    id: int
    title: str
    tag: Optional[str] = None
    body: str
    date: Optional[str] = None
    status: NewsStatus
    publish_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    author_id: Optional[int] = None
    views_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
