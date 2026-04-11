from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Enum as SAEnum, ForeignKey, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class NewsStatus(str, enum.Enum):
    draft = "draft"           # черновик — не виден на сайте
    review = "review"         # на модерации у редактора
    scheduled = "scheduled"   # запланирован к публикации в publish_at
    published = "published"   # опубликован — виден всем
    archived = "archived"     # архив — скрыт


# Допустимые переходы статусов (FSM)
NEWS_STATUS_TRANSITIONS: dict[NewsStatus, list[NewsStatus]] = {
    NewsStatus.draft:     [NewsStatus.review, NewsStatus.scheduled, NewsStatus.published],
    NewsStatus.review:    [NewsStatus.draft, NewsStatus.scheduled, NewsStatus.published, NewsStatus.archived],
    NewsStatus.scheduled: [NewsStatus.draft, NewsStatus.published, NewsStatus.archived],
    NewsStatus.published: [NewsStatus.archived],
    NewsStatus.archived:  [NewsStatus.draft],
}


class NewsCategory(Base):
    """Категории статей (новости, акции, события, объявления ...)"""
    __tablename__ = "news_categories"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False, unique=True)
    slug       = Column(String(100), nullable=False, unique=True)  # url-friendly
    color      = Column(String(20), nullable=True)   # HEX-цвет для UI-бейджа
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="category", lazy="selectin")


class NewsStatusHistory(Base):
    """Журнал переходов статусов — кто, когда и из какого статуса"""
    __tablename__ = "news_status_history"

    id         = Column(Integer, primary_key=True, index=True)
    news_id    = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(SAEnum(NewsStatus), nullable=True)  # None при создании
    to_status  = Column(SAEnum(NewsStatus), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    comment    = Column(String(500), nullable=True)  # причина отклонения / заметка
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="status_history")


class NewsLike(Base):
    """Лайки новостей — один пользователь = один лайк на новость"""
    __tablename__ = "news_likes"
    __table_args__ = (UniqueConstraint("news_id", "user_id", name="uq_news_like"),)

    id      = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="likes")


class News(Base):
    __tablename__ = "news"

    id    = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug  = Column(String(300), nullable=True, unique=True, index=True)  # SEO-URL
    tag   = Column(String(100), nullable=True)   # свободный тег (обратная совместимость)
    body  = Column(Text, nullable=False)
    date  = Column(String(20), nullable=True)    # форматированная дата для фронта
    image_url = Column(String(500), nullable=True)  # обложка статьи
    is_pinned = Column(Boolean, default=False)       # закреплённая новость вверху

    # Статус и даты публикации
    status       = Column(SAEnum(NewsStatus), nullable=False, default=NewsStatus.draft, index=True)
    publish_at   = Column(DateTime, nullable=True)   # отложенная публикация
    published_at = Column(DateTime, nullable=True)   # фактическая дата публикации

    # Связи
    author_id   = Column(Integer, ForeignKey("users.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("news_categories.id"), nullable=True)

    # Счётчики
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)  # денормализованный счётчик для скорости

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category       = relationship("NewsCategory", back_populates="news", lazy="selectin")
    status_history = relationship(
        "NewsStatusHistory", back_populates="news",
        order_by="NewsStatusHistory.created_at", cascade="all, delete-orphan", lazy="selectin"
    )
    likes = relationship(
        "NewsLike", back_populates="news",
        cascade="all, delete-orphan", lazy="selectin"
    )
