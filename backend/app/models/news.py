from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum, ForeignKey
from app.core.database import Base
import enum


class NewsStatus(str, enum.Enum):
    draft = "draft"           # черновик — не виден на сайте
    review = "review"         # на модерации
    scheduled = "scheduled"   # запланирован к публикации в publish_at
    published = "published"   # опубликован — виден всем
    archived = "archived"     # архив — скрыт


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    tag = Column(String(100), nullable=True)
    body = Column(Text, nullable=False)
    date = Column(String(20), nullable=True)

    # Новые поля статуса и публикации
    status = Column(SAEnum(NewsStatus), nullable=False, default=NewsStatus.draft)
    publish_at = Column(DateTime, nullable=True)   # дата отложенной публикации
    published_at = Column(DateTime, nullable=True) # фактическая дата публикации
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    views_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
