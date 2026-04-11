"""API для просмотра audit_log.

Новое по сравнению с предыдущей версией:
  + Пагинация (page / page_size) с возвратом total
  + Фильтр по user_id, периоду (since/until), status_code
  + Эндпоинт /audit/{id} для подробной записи
  + Функция write_audit_log() для ручной записи (LOGIN, спец. действия)
"""
from datetime import datetime
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


# ── Схемы ───────────────────────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int]    = None
    user_email: Optional[str] = None
    user_role: Optional[str]  = None
    action: str
    entity_type: str
    entity_id: Optional[int]  = None
    http_method: Optional[str]  = None
    endpoint: Optional[str]     = None
    status_code: Optional[int]  = None
    duration_ms: Optional[int]  = None
    user_agent: Optional[str]   = None
    ip_address: Optional[str]   = None
    request_body: Optional[str] = None
    old_value: Optional[str]    = None
    new_value: Optional[str]    = None
    details: Optional[str]      = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListOut(BaseModel):
    total: int
    pages: int
    page: int
    items: List[AuditLogOut]


# ── Вспомогательная функция (ручная запись) ─────────────────────────────
async def write_audit_log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    user_role: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
) -> None:
    """Импортируется и вызывается вручную из роутеров.

    Используется для: LOGIN, смены пароля, специфичных действий с old/new.
    commit() делает вызывающий роутер.
    """
    db.add(AuditLog(
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
        old_value=old_value,
        new_value=new_value,
    ))


# ── Эндпоинты ───────────────────────────────────────────────────────────────────
@router.get("/", response_model=AuditLogListOut, summary="[Админ] Журнал действий")
async def get_audit_log(
    entity_type: Optional[str]  = Query(None, description="Фильтр по типу: news, groups, payments…"),
    action:      Optional[str]  = Query(None, description="Фильтр по действию: CREATE, UPDATE, DELETE, LOGIN…"),
    user_id:     Optional[int]  = Query(None, description="Фильтр по пользователю"),
    status_code: Optional[int]  = Query(None, description="Фильтр по HTTP-коду ответа"),
    since:       Optional[datetime] = Query(None, description="Начало периода (ISO 8601)"),
    until:       Optional[datetime] = Query(None, description="Конец периода (ISO 8601)"),
    page:        int = Query(1,  ge=1),
    page_size:   int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Журнал действий с пагинацией и множественными фильтрами."""
    q = select(AuditLog)
    if entity_type:  q = q.where(AuditLog.entity_type == entity_type)
    if action:       q = q.where(AuditLog.action      == action)
    if user_id:      q = q.where(AuditLog.user_id     == user_id)
    if status_code:  q = q.where(AuditLog.status_code == status_code)
    if since:        q = q.where(AuditLog.created_at  >= since)
    if until:        q = q.where(AuditLog.created_at  <= until)

    # Подсчёт общего количества
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()

    # Данные страницы
    items_q = q.order_by(AuditLog.created_at.desc())
    items_q = items_q.offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_q)).scalars().all()

    return AuditLogListOut(
        total=total,
        pages=ceil(total / page_size) if total else 0,
        page=page,
        items=items,
    )


@router.get("/{log_id}", response_model=AuditLogOut, summary="[Админ] Подробная запись")
async def get_audit_entry(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return entry


@router.get("/stats/summary", summary="[Админ] Статистика журнала")
async def audit_stats(
    since: Optional[datetime] = Query(None),
    db: AsyncSession  = Depends(get_db),
    _=Depends(require_admin),
):
    """Количество записей по каждому action за выбранный период."""
    q = select(AuditLog.action, func.count(AuditLog.id).label("cnt"))
    if since:
        q = q.where(AuditLog.created_at >= since)
    q = q.group_by(AuditLog.action).order_by(func.count(AuditLog.id).desc())
    rows = await db.execute(q)
    return {"by_action": {row.action: row.cnt for row in rows}}
