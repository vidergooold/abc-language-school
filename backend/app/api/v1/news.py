from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.news import News, NewsStatus
from app.schemas.news import NewsCreate, NewsUpdate, NewsOut

router = APIRouter(tags=["News"])


@router.get("/news", response_model=List[NewsOut])
async def get_news(db: AsyncSession = Depends(get_db)):
    """Публичный список: только опубликованные новости"""
    result = await db.execute(
        select(News)
        .where(News.status == NewsStatus.published)
        .order_by(News.published_at.desc())
    )
    return result.scalars().all()


@router.get("/news/{news_id}", response_model=NewsOut)
async def get_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    """Получить одну новость (только опубликованную)"""
    result = await db.execute(
        select(News).where(News.id == news_id, News.status == NewsStatus.published)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    # Увеличиваем счётчик просмотров
    news.views_count = (news.views_count or 0) + 1
    await db.commit()
    await db.refresh(news)
    return news


@router.get("/admin/news", response_model=List[NewsOut])
async def admin_get_news(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Все новости для администратора — включая черновики, на модерации, архив"""
    result = await db.execute(select(News).order_by(News.created_at.desc()))
    return result.scalars().all()


@router.post("/admin/news", response_model=NewsOut)
async def admin_create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Создать новость.
    Статусы:
      draft      — черновик, виден только в админке
      review     — отправлен на проверку
      scheduled  — будет опубликован в publish_at
      published  — виден всем на сайте (published_at = now)
    """
    publish_time = None
    if data.status == NewsStatus.published:
        publish_time = datetime.utcnow()

    news = News(
        title=data.title,
        tag=data.tag,
        body=data.body,
        status=data.status,
        publish_at=data.publish_at,
        published_at=publish_time,
        date=datetime.utcnow().strftime("%d.%m.%Y"),
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


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
    if data.publish_at is not None:
        news.publish_at = data.publish_at

    # При смене статуса на published — фиксируем время публикации
    if data.status is not None and data.status != news.status:
        news.status = data.status
        if data.status == NewsStatus.published and not news.published_at:
            news.published_at = datetime.utcnow()
        elif data.status == NewsStatus.archived:
            pass  # архивируем без изменения published_at

    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/publish", response_model=NewsOut)
async def admin_publish_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Явная публикация новости (draft/review → published)"""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    if news.status == NewsStatus.published:
        raise HTTPException(status_code=400, detail="Новость уже опубликована")
    news.status = NewsStatus.published
    news.published_at = datetime.utcnow()
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/archive", response_model=NewsOut)
async def admin_archive_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Перевести новость в архив"""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    news.status = NewsStatus.archived
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/publish-scheduled")
async def publish_scheduled_news(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Публикует все новости со статусом 'scheduled', у которых publish_at <= now.
    Вызывается планировщиком автоматически или вручную администратором.
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(News).where(
            News.status == NewsStatus.scheduled,
            News.publish_at <= now,
        )
    )
    news_list = result.scalars().all()
    published = []
    for news in news_list:
        news.status = NewsStatus.published
        news.published_at = now
        published.append(news.title)
    await db.commit()
    return {"published": len(published), "titles": published}


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
