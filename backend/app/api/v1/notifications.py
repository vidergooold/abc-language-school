from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.notification import Notification, NotificationQueue, NotificationStatus, NotificationType
from app.models.group import StudentGroup
from app.schemas.notification import NotificationCreate, NotificationOut, BulkNotificationCreate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


async def _simulate_send(notification_id: int, recipient: str, message: str):
    """
    Имитация отправки уведомления.
    В production здесь будет вызов SMTP / Telegram Bot API / SMS-шлюза.
    Сейчас просто логирует и помечает как отправленное.
    """
    print(f"[NOTIFICATION] Отправка на {recipient}: {message[:80]}...")


@router.post("/", response_model=NotificationOut)
async def create_notification(
    data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Создать уведомление.
    Если scheduled_at не задан — помещается в очередь немедленно.
    Если задан — помещается в очередь с отложенной отправкой.
    """
    notification = Notification(
        title=data.title,
        body=data.body,
        notification_type=data.notification_type,
        channel=data.channel,
        recipient_email=data.recipient_email,
        recipient_phone=data.recipient_phone,
        recipient_name=data.recipient_name,
        scheduled_at=data.scheduled_at,
        status=NotificationStatus.pending,
    )
    db.add(notification)
    await db.flush()  # получаем ID

    # Помещаем в очередь
    queue_item = NotificationQueue(
        notification_id=notification.id,
        recipient_email=data.recipient_email,
        recipient_phone=data.recipient_phone,
        recipient_name=data.recipient_name,
        subject=data.title,
        message=data.body,
        channel=data.channel,
        scheduled_at=data.scheduled_at or datetime.utcnow(),
        status=NotificationStatus.pending,
    )
    db.add(queue_item)
    await db.commit()
    await db.refresh(notification)

    # Если без задержки — фоновая задача
    if not data.scheduled_at:
        background_tasks.add_task(
            _simulate_send,
            notification.id,
            data.recipient_email or data.recipient_phone or "unknown",
            data.body,
        )

    return notification


@router.post("/bulk")
async def send_bulk_notification(
    data: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Массовая рассылка всем активным студентам группы.
    Создаёт отдельную запись Notification + NotificationQueue для каждого студента.
    """
    students_result = await db.execute(
        select(StudentGroup)
        .where(StudentGroup.group_id == data.group_id, StudentGroup.is_active == True)
    )
    students = students_result.scalars().all()

    if not students:
        raise HTTPException(status_code=404, detail="В группе нет активных студентов")

    sent_to = []
    for student in students:
        notification = Notification(
            title=data.title,
            body=data.body,
            notification_type=NotificationType.custom,
            channel=data.channel,
            recipient_email=student.student_email,
            recipient_phone=student.student_phone,
            recipient_name=student.student_name,
            scheduled_at=data.scheduled_at,
            status=NotificationStatus.pending,
        )
        db.add(notification)
        await db.flush()

        queue_item = NotificationQueue(
            notification_id=notification.id,
            recipient_email=student.student_email,
            recipient_phone=student.student_phone,
            recipient_name=student.student_name,
            subject=data.title,
            message=data.body,
            channel=data.channel,
            scheduled_at=data.scheduled_at or datetime.utcnow(),
            status=NotificationStatus.pending,
        )
        db.add(queue_item)
        sent_to.append(student.student_name)

    await db.commit()
    return {
        "queued": len(sent_to),
        "recipients": sent_to,
        "scheduled_at": data.scheduled_at,
    }


@router.get("/queue", response_model=List[NotificationOut])
async def get_notification_queue(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Просмотр очереди уведомлений"""
    result = await db.execute(
        select(Notification)
        .where(Notification.status == NotificationStatus.pending)
        .order_by(Notification.scheduled_at)
    )
    return result.scalars().all()


@router.post("/process-queue")
async def process_notification_queue(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Обработка очереди уведомлений вручную (или вызывается планировщиком).
    Находит все pending-уведомления с scheduled_at <= now и отправляет их.
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(NotificationQueue).where(
            and_(
                NotificationQueue.status == NotificationStatus.pending,
                NotificationQueue.scheduled_at <= now,
            )
        )
    )
    queue_items = result.scalars().all()

    processed = 0
    for item in queue_items:
        item.status = NotificationStatus.sent
        item.sent_at = now
        background_tasks.add_task(
            _simulate_send,
            item.id,
            item.recipient_email or item.recipient_phone or "unknown",
            item.message,
        )
        processed += 1

    await db.commit()
    return {"processed": processed, "timestamp": now.isoformat()}
