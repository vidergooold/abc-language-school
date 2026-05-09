from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_auth
from app.models.message import Message
from app.models.user import User, UserRole
from app.schemas.message import MessageCreate, MessageRead, UnreadCount

router = APIRouter(prefix="/messages", tags=["Messages"])


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

@router.get("", response_model=List[MessageRead])
@router.get("/", response_model=List[MessageRead])
async def list_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Все сообщения, где текущий пользователь является отправителем или получателем."""
    result = await db.execute(
        select(Message)
        .where(
            or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Отправить сообщение администратору. Только для преподавателей."""
    if current_user.role != UserRole.teacher:
        raise HTTPException(status_code=403, detail="Только преподаватели могут отправлять сообщения")
    admin = await _get_admin(db)
    item = Message(
        sender_id=current_user.id,
        recipient_id=admin.id,
        body=payload.body,
        is_read=False,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/inbox", response_model=List[MessageRead])
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


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Количество непрочитанных сообщений для текущего пользователя."""
    result = await db.execute(
        select(func.count(Message.id)).where(
            Message.recipient_id == current_user.id,
            Message.is_read.is_(False),
        )
    )
    return {"unread": result.scalar() or 0}


@router.patch("/{message_id}/read", response_model=MessageRead)
async def mark_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Пометить сообщение как прочитанное. Только получатель."""
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.recipient_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    item.is_read = True
    await db.commit()
    await db.refresh(item)
    return item
