from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_auth
from app.models.message import Message
from app.models.user import User, UserRole

router = APIRouter(prefix="/messages", tags=["Messages"])


# ─── Pydantic схемы ──────────────────────────────────────────────

class MessageCreate(BaseModel):
    body: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Вспомогательная функция ─────────────────────────────────────

async def _get_admin(db: AsyncSession) -> User:
    """Возвращает первого активного администратора."""
    result = await db.execute(
        select(User).where(User.role == UserRole.admin, User.is_active == True)
    )
    admin = result.scalars().first()
    if not admin:
        raise HTTPException(status_code=404, detail="Администратор не найден")
    return admin


# ─── Эндпоинты ───────────────────────────────────────────────────

@router.post("/", response_model=MessageOut, status_code=201)
async def send_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Отправить сообщение администратору. Только для преподавателей."""
    if current_user.role != UserRole.teacher:
        raise HTTPException(status_code=403, detail="Только преподаватели могут отправлять сообщения")
    admin = await _get_admin(db)
    msg = Message(sender_id=current_user.id, recipient_id=admin.id, body=data.body)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get("/inbox", response_model=List[MessageOut])
async def get_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Входящие сообщения текущего пользователя, отсортированные по дате (новые первыми)."""
    result = await db.execute(
        select(Message)
        .where(Message.recipient_id == current_user.id)
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{message_id}/read", response_model=MessageOut)
async def mark_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Пометить сообщение как прочитанное. Только получатель."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    if msg.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому сообщению")
    msg.is_read = True
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Количество непрочитанных сообщений для текущего пользователя."""
    count = await db.scalar(
        select(func.count()).select_from(Message).where(
            Message.recipient_id == current_user.id,
            Message.is_read == False,
        )
    )
    return {"unread": count or 0}
