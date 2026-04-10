from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.core.security import require_admin
from app.models.waitlist import WaitlistEntry, WaitlistStatus
from app.models.group import StudentGroup, Group
from app.models.notification import Notification, NotificationQueue, NotificationStatus, NotificationType, NotificationChannel
from app.schemas.waitlist import WaitlistCreate, WaitlistOut

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


@router.get("/", response_model=List[WaitlistOut])
async def get_waitlist(
    course_id: int = None,
    group_id: int = None,
    status: WaitlistStatus = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Получить лист ожидания с фильтрами по курсу, группе, статусу."""
    query = select(WaitlistEntry).order_by(WaitlistEntry.position)
    if course_id:
        query = query.where(WaitlistEntry.course_id == course_id)
    if group_id:
        query = query.where(WaitlistEntry.group_id == group_id)
    if status:
        query = query.where(WaitlistEntry.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=WaitlistOut)
async def add_to_waitlist(
    data: WaitlistCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Добавить в лист ожидания.
    Позиция назначается автоматически: max(position)+1 для данного курса.
    """
    max_pos_result = await db.execute(
        select(func.max(WaitlistEntry.position)).where(
            WaitlistEntry.course_id == data.course_id,
            WaitlistEntry.status == WaitlistStatus.waiting,
        )
    )
    max_pos = max_pos_result.scalar() or 0

    entry = WaitlistEntry(**data.model_dump(), position=max_pos + 1)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/{entry_id}/notify")
async def notify_waitlist_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Уведомить первого в очереди о появлении места.
    Меняет статус на notified и создаёт уведомление.
    """
    result = await db.execute(select(WaitlistEntry).where(WaitlistEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    if entry.status != WaitlistStatus.waiting:
        raise HTTPException(status_code=400, detail=f"Статус уже: {entry.status}")

    entry.status = WaitlistStatus.notified
    entry.notified_at = datetime.utcnow()

    # Создаём уведомление
    notif = Notification(
        title="Место в группе освободилось!",
        body=(
            f"Уважаемый(ая) {entry.student_name}, для вас освободилось место. "
            "Пожалуйста, свяжитесь с нами для подтверждения записи."
        ),
        notification_type=NotificationType.enrollment_confirm,
        channel=NotificationChannel.email,
        recipient_email=entry.student_email,
        recipient_phone=entry.student_phone,
        recipient_name=entry.student_name,
        status=NotificationStatus.pending,
    )
    db.add(notif)
    await db.flush()

    queue_item = NotificationQueue(
        notification_id=notif.id,
        recipient_email=entry.student_email,
        recipient_phone=entry.student_phone,
        recipient_name=entry.student_name,
        subject=notif.title,
        message=notif.body,
        channel=NotificationChannel.email,
        scheduled_at=datetime.utcnow(),
        status=NotificationStatus.pending,
    )
    db.add(queue_item)
    await db.commit()
    return {"ok": True, "notified": entry.student_name}


@router.post("/{entry_id}/enroll")
async def enroll_from_waitlist(
    entry_id: int,
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Зачислить студента из листа ожидания в группу.
    1. Проверяем, что в группе есть место.
    2. Создаём StudentGroup.
    3. Меняем статус WaitlistEntry → enrolled.
    4. Пересчитываем позиции оставшихся в очереди.
    """
    result = await db.execute(select(WaitlistEntry).where(WaitlistEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    # Проверяем лимит группы
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    from app.models.group import Course
    course_result = await db.execute(select(Course).where(Course.id == group.course_id))
    course = course_result.scalar_one_or_none()

    current_count = await db.scalar(
        select(func.count()).select_from(StudentGroup)
        .where(StudentGroup.group_id == group_id, StudentGroup.is_active == True)
    )
    if course and current_count >= course.max_students:
        raise HTTPException(status_code=400, detail="В группе нет свободных мест")

    # Зачисляем
    student_group = StudentGroup(
        group_id=group_id,
        student_name=entry.student_name,
        student_phone=entry.student_phone,
        student_email=entry.student_email,
        student_type=entry.student_type,
    )
    db.add(student_group)

    entry.status = WaitlistStatus.enrolled
    entry.enrolled_at = datetime.utcnow()

    # Пересчёт позиций — сдвигаем оставшихся в очереди
    remaining_result = await db.execute(
        select(WaitlistEntry).where(
            and_(
                WaitlistEntry.course_id == entry.course_id,
                WaitlistEntry.status == WaitlistStatus.waiting,
                WaitlistEntry.position > entry.position,
            )
        ).order_by(WaitlistEntry.position)
    )
    for remaining in remaining_result.scalars().all():
        remaining.position -= 1

    await db.commit()
    return {"ok": True, "enrolled": entry.student_name, "group_id": group_id}


@router.delete("/{entry_id}")
async def remove_from_waitlist(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Удалить из листа ожидания и пересчитать позиции."""
    result = await db.execute(select(WaitlistEntry).where(WaitlistEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    entry.status = WaitlistStatus.cancelled

    remaining_result = await db.execute(
        select(WaitlistEntry).where(
            and_(
                WaitlistEntry.course_id == entry.course_id,
                WaitlistEntry.status == WaitlistStatus.waiting,
                WaitlistEntry.position > entry.position,
            )
        )
    )
    for remaining in remaining_result.scalars().all():
        remaining.position -= 1

    await db.commit()
    return {"ok": True}
