from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.news import NewsStatus


# ── Категории ────────────────────────────────────────────────────────────────
class NewsCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=20)


class NewsCategoryCreate(NewsCategoryBase):
    pass


class NewsCategoryOut(NewsCategoryBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── История статусов ───────────────────────────────────────────────────────────────
class NewsStatusHistoryOut(BaseModel):
    id: int
    from_status: Optional[NewsStatus]
    to_status: NewsStatus
    changed_by: Optional[int]
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Новости ──────────────────────────────────────────────────────────────────
class NewsCreate(BaseModel):
    title: str = Field(..., max_length=255)
    tag: Optional[str] = Field(None, max_length=100)
    body: str
    status: NewsStatus = NewsStatus.draft
    publish_at: Optional[datetime] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_pinned: bool = False


class NewsUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    tag: Optional[str] = Field(None, max_length=100)
    body: Optional[str] = None
    status: Optional[NewsStatus] = None
    publish_at: Optional[datetime] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_pinned: Optional[bool] = None
    comment: Optional[str] = Field(None, max_length=500)


class NewsOut(BaseModel):
    id: int
    title: str
    slug: Optional[str]
    tag: Optional[str]
    body: str
    date: Optional[str]
    image_url: Optional[str]
    is_pinned: Optional[bool] = False
    status: NewsStatus
    publish_at: Optional[datetime]
    published_at: Optional[datetime]
    author_id: Optional[int]
    category_id: Optional[int]
    category: Optional[NewsCategoryOut]
    views_count: Optional[int] = 0
    likes_count: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_history: List[NewsStatusHistoryOut] = []

    model_config = {"from_attributes": True}

    @field_validator("is_pinned", mode="before")
    @classmethod
    def coerce_is_pinned(cls, v):
        return v if v is not None else False

    @field_validator("views_count", "likes_count", mode="before")
    @classmethod
    def coerce_counts(cls, v):
        return v if v is not None else 0


class NewsListOut(BaseModel):
    """\u041e\u0431\u043b\u0435\u0433\u0447\u0451\u043d\u043d\u044b\u0439 \u0432\u044b\u0432\u043e\u0434 \u0434\u043b\u044f \u0441\u043f\u0438\u0441\u043a\u043e\u0432 — \u0431\u0435\u0437 body \u0438 \u0438\u0441\u0442\u043e\u0440\u0438\u0438"""
    id: int
    title: str
    slug: Optional[str]
    tag: Optional[str]
    date: Optional[str]
    image_url: Optional[str]
    is_pinned: Optional[bool] = False
    status: NewsStatus
    published_at: Optional[datetime]
    category: Optional[NewsCategoryOut]
    views_count: Optional[int] = 0
    likes_count: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator("is_pinned", mode="before")
    @classmethod
    def coerce_is_pinned(cls, v):
        return v if v is not None else False

    @field_validator("views_count", "likes_count", mode="before")
    @classmethod
    def coerce_counts(cls, v):
        return v if v is not None else 0


class NewsPaginatedOut(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[NewsListOut]
