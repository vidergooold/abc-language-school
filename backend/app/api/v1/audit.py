from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import require_admin
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


async def write_audit_log(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: int = None,
    user_id: int = None,
    user_email: str = None,
    details: str = None,
    ip_address: str = None,
):
    """
    Вспомогательная функция для записи в журнал.
    Импортируется и вызывается из любого роута при CREATE/UPDATE/DELETE.
    """
    log = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    # Не делаем commit здесь — он будет в вызывающем роуте


@router.get("/", response_model=List[AuditLogOut])
async def get_audit_log(
    entity_type: str = Query(None),
    action: str = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Журнал действий. Можно фильтровать по типу сущности и действию."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if action:
        query = query.where(AuditLog.action == action)
    result = await db.execute(query)
    return result.scalars().all()
