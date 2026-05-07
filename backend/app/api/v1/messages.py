from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_student
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageRead, UnreadCount

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/", response_model=List[MessageRead])
async def list_messages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
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
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    recipient = await db.get(User, payload.recipient_id)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    item = Message(
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        body=payload.body,
        is_read=False,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/unread-count", response_model=UnreadCount)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    result = await db.execute(
        select(func.count(Message.id)).where(
            Message.recipient_id == current_user.id,
            Message.is_read.is_(False),
        )
    )
    return {"unread": result.scalar() or 0}


@router.patch("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.recipient_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Message not found")

    item.is_read = True
    await db.commit()
    return {"ok": True}
