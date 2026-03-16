from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.news import News
from app.schemas.news import NewsCreate, NewsUpdate, NewsOut

router = APIRouter(tags=["News"])


# Публичный список новостей
@router.get("/news", response_model=List[NewsOut])
async def get_news(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(News).order_by(News.created_at.desc()))
    return result.scalars().all()


# Админ: список
@router.get("/admin/news", response_model=List[NewsOut])
async def admin_get_news(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(News).order_by(News.created_at.desc()))
    return result.scalars().all()


# Админ: создать
@router.post("/admin/news", response_model=NewsOut)
async def admin_create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    news = News(
        title=data.title,
        tag=data.tag,
        body=data.body,
        date=datetime.utcnow().strftime("%d.%m.%Y"),
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


# Админ: редактировать
@router.put("/admin/news/{news_id}", response_model=NewsOut)
async def admin_update_news(
    news_id: int,
    data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    if data.title is not None:
        news.title = data.title
    if data.tag is not None:
        news.tag = data.tag
    if data.body is not None:
        news.body = data.body
    await db.commit()
    await db.refresh(news)
    return news


# Админ: удалить
@router.delete("/admin/news/{news_id}")
async def admin_delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await db.delete(news)
    await db.commit()
    return {"ok": True}
