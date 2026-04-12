"""Модуль новостей / статей.

Функциональность:
  - Публичное API: список (пагинация, фильтр по тегу/категории/статусу),
    получение одной статьи, лайк/анлайк.
  - Административное API: CRUD, смена статуса с FSM-проверкой,
    ручная и автоматическая (планировщик) публикация запланированных статей.
  - История переходов статусов с указанием автора и комментарием.

Statuses FSM:
  draft → review → scheduled → published → archived → draft
  (подробнее: NEWS_STATUS_TRANSITIONS в models/news.py)
"""
from datetime import datetime
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.news import News, NewsCategory, NewsLike, NewsStatusHistory, NEWS_STATUS_TRANSITIONS, NewsStatus
from app.models.user import User
from app.schemas.news import (
    NewsCreate, NewsUpdate, NewsOut, NewsListOut, NewsPaginatedOut,
    NewsCategoryCreate, NewsCategoryOut,
)

router = APIRouter(tags=["News"])


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════

def _make_slug(title: str, news_id: int) -> str:
    """Генерирует простой slug из заголовка + id."""
    import re
    slug = title.lower().strip()
    slug = re.sub(r'[^а-яёa-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return f"{slug}-{news_id}"


async def _record_status_change(
    db: AsyncSession,
    news: News,
    new_status: NewsStatus,
    user_id: Optional[int],
    comment: Optional[str] = None,
) -> None:
    """Записывает переход статуса в историю и применяет к объекту."""
    # FSM-проверка
    allowed = NEWS_STATUS_TRANSITIONS.get(news.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Переход '{news.status}' → '{new_status}' запрещён. "
                f"Разрешённые: {[s.value for s in allowed]}"
            ),
        )
    history = NewsStatusHistory(
        news_id=news.id,
        from_status=news.status,
        to_status=new_status,
        changed_by=user_id,
        comment=comment,
    )
    db.add(history)
    news.status = new_status
    if new_status == NewsStatus.published and not news.published_at:
        news.published_at = datetime.utcnow()


# ═══════════════════════════════════════════════════════════════════════
# ПУБЛИЧНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/news", response_model=NewsPaginatedOut, summary="Список опубликованных новостей")
async def get_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: Optional[str] = Query(None, description="Фильтр по тегу"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    pinned_first: bool = Query(True, description="Закреплённые вверху"),
    db: AsyncSession = Depends(get_db),
):
    """Публичный список — только опубликованные. Поддерживает пагинацию и фильтры."""
    q = select(News).where(News.status == NewsStatus.published)
    if tag:
        q = q.where(News.tag == tag)
    if category_id:
        q = q.where(News.category_id == category_id)

    # Счётчик
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Сортировка
    order_cols = []
    if pinned_first:
        order_cols.append(News.is_pinned.desc())
    order_cols.append(News.published_at.desc())
    q = q.order_by(*order_cols).offset((page - 1) * page_size).limit(page_size)

    items = (await db.execute(q)).scalars().all()
    return NewsPaginatedOut(
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total else 1,
        items=items,
    )


@router.get("/news/{news_id}", response_model=NewsOut, summary="Одна новость")
async def get_news_item(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Публичный доступ — только опубликованная. Увеличивает счётчик просмотров."""
    result = await db.execute(
        select(News).where(News.id == news_id, News.status == NewsStatus.published)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    news.views_count = (news.views_count or 0) + 1
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/news/{news_id}/like", summary="Поставить / убрать лайк")
async def toggle_like(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Авторизованный пользователь ставит или убирает лайк (toggle)."""
    result = await db.execute(
        select(News).where(News.id == news_id, News.status == NewsStatus.published)
    )
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    existing = await db.execute(
        select(NewsLike).where(NewsLike.news_id == news_id, NewsLike.user_id == current_user.id)
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        news.likes_count = max(0, (news.likes_count or 1) - 1)
        action = "unliked"
    else:
        db.add(NewsLike(news_id=news_id, user_id=current_user.id))
        news.likes_count = (news.likes_count or 0) + 1
        action = "liked"

    await db.commit()
    return {"action": action, "likes_count": news.likes_count}


# ═══════════════════════════════════════════════════════════════════════
# АДМИНИСТРАТИВНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/admin/news", response_model=List[NewsOut], summary="[Админ] Все новости")
async def admin_get_news(
    status_filter: Optional[NewsStatus] = Query(None, alias="status"),
    category_id: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Все новости для администратора — черновики, на модерации, архив."""
    q = select(News)
    if status_filter:
        q = q.where(News.status == status_filter)
    if category_id:
        q = q.where(News.category_id == category_id)
    if tag:
        q = q.where(News.tag == tag)
    q = q.order_by(News.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/admin/news", response_model=NewsOut, status_code=201, summary="[Админ] Создать новость")
async def admin_create_news(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Создать новость. Начальный статус фиксируется в истории переходов.
    При статусе published — сразу устанавливается published_at.
    """
    publish_time = datetime.utcnow() if data.status == NewsStatus.published else None

    news = News(
        title=data.title,
        tag=data.tag,
        body=data.body,
        status=data.status,
        publish_at=data.publish_at.replace(tzinfo=None) if data.publish_at else None,
        published_at=publish_time,
        category_id=data.category_id,
        image_url=data.image_url,
        is_pinned=data.is_pinned,
        author_id=current_user.id,
        date=datetime.utcnow().strftime("%d.%m.%Y"),
    )
    db.add(news)
    await db.flush()  # получаем id до commit

    # Генерируем slug
    news.slug = _make_slug(data.title, news.id)

    # Записываем первый переход в историю (создание → начальный статус)
    history = NewsStatusHistory(
        news_id=news.id,
        from_status=None,
        to_status=data.status,
        changed_by=current_user.id,
        comment="Создание статьи",
    )
    db.add(history)
    await db.commit()
    await db.refresh(news)
    return news


@router.put("/admin/news/{news_id}", response_model=NewsOut, summary="[Админ] Обновить новость")
async def admin_update_news(
    news_id: int,
    data: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Обновление полей. Смена статуса проходит через FSM с записью в историю."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")

    if data.title is not None:
        news.title = data.title
        news.slug = _make_slug(data.title, news.id)
    if data.tag is not None:
        news.tag = data.tag
    if data.body is not None:
        news.body = data.body
    if data.publish_at is not None:
        news.publish_at = data.publish_at.replace(tzinfo=None) if data.publish_at else None
    if data.category_id is not None:
        news.category_id = data.category_id
    if data.image_url is not None:
        news.image_url = data.image_url
    if data.is_pinned is not None:
        news.is_pinned = data.is_pinned

    # Смена статуса через FSM
    if data.status is not None and data.status != news.status:
        await _record_status_change(db, news, data.status, current_user.id, data.comment)

    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/publish", response_model=NewsOut, summary="[Админ] Опубликовать")
async def admin_publish_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Явная публикация (draft/review/scheduled → published) через FSM."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await _record_status_change(db, news, NewsStatus.published, current_user.id, "Ручная публикация")
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/archive", response_model=NewsOut, summary="[Админ] Архивировать")
async def admin_archive_news(
    news_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Перевод в архив через FSM. Можно оставить комментарий."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await _record_status_change(db, news, NewsStatus.archived, current_user.id, comment)
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/send-to-review", response_model=NewsOut, summary="[Админ] На модерацию")
async def admin_send_to_review(
    news_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Отправить черновик на проверку редактору (draft → review)."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await _record_status_change(db, news, NewsStatus.review, current_user.id, comment)
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/reject", response_model=NewsOut, summary="[Админ] Отклонить (review → draft)")
async def admin_reject_news(
    news_id: int,
    comment: str = Query(..., description="Причина отклонения"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Отклонить статью на модерации — вернуть в черновик с комментарием."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    await _record_status_change(db, news, NewsStatus.draft, current_user.id, comment)
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/{news_id}/pin", response_model=NewsOut, summary="[Админ] Закрепить / открепить")
async def admin_toggle_pin(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Переключить флаг is_pinned (закреплённая новость всегда идёт первой)."""
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    news.is_pinned = not news.is_pinned
    await db.commit()
    await db.refresh(news)
    return news


@router.post("/admin/news/publish-scheduled", summary="[Планировщик] Опубликовать запланированные")
async def publish_scheduled_news(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Публикует все scheduled-статьи, у которых publish_at <= now.
    Вызывается APScheduler автоматически каждые 5 минут.
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(News).where(News.status == NewsStatus.scheduled, News.publish_at <= now)
    )
    news_list = result.scalars().all()
    published_titles = []
    for news in news_list:
        # FSM разрешает scheduled → published
        news.status = NewsStatus.published
        news.published_at = now
        db.add(NewsStatusHistory(
            news_id=news.id,
            from_status=NewsStatus.scheduled,
            to_status=NewsStatus.published,
            changed_by=None,  # автоматически, без пользователя
            comment="Автоматическая публикация по расписанию",
        ))
        published_titles.append(news.title)
    await db.commit()
    return {"published": len(published_titles), "titles": published_titles}


@router.delete("/admin/news/{news_id}", summary="[Админ] Удалить новость")
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


# ═══════════════════════════════════════════════════════════════════════
# КАТЕГОРИИ
# ═══════════════════════════════════════════════════════════════════════

@router.get("/news/categories", response_model=List[NewsCategoryOut], summary="Список категорий")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsCategory).order_by(NewsCategory.name))
    return result.scalars().all()


@router.post("/admin/news/categories", response_model=NewsCategoryOut, status_code=201, summary="[Админ] Создать категорию")
async def admin_create_category(
    data: NewsCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    # Проверка уникальности slug
    existing = await db.execute(select(NewsCategory).where(NewsCategory.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Категория с таким slug уже существует")
    category = NewsCategory(name=data.name, slug=data.slug, color=data.color)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/admin/news/categories/{category_id}", summary="[Админ] Удалить категорию")
async def admin_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(NewsCategory).where(NewsCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    await db.delete(category)
    await db.commit()
    return {"ok": True}
