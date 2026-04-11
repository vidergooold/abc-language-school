"""Модуль заявок на зачисление.

Цикл заявки (FSM):

  pending
    ↓ подтверждение администратором
  confirmed
    ↓ запись в группу (StudentGroup) + авто Invoice
  awaiting_payment
    ↓ факт оплаты (Invoice.status = paid)
  active
    ↓ отчисление по желанию
  withdrawn

Альтернативы: cancelled (админ), rejected (нет мест/уровень).
"""
from datetime import datetime, timedelta
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.enrollment import (
    Enrollment, EnrollmentStatus, EnrollmentStatusHistory,
    ENROLLMENT_STATUS_TRANSITIONS,
)
from app.models.group import Group, StudentGroup
from app.models.payment import Invoice, PaymentStatus
from app.models.user import User
from app.schemas.enrollment import (
    EnrollmentCreate, EnrollmentResponse, EnrollmentOut, EnrollmentListOut,
    EnrollmentConfirm, EnrollmentAssignGroup, EnrollmentReject, EnrollmentWithdraw,
)

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════

async def _get_enrollment_or_404(enrollment_id: int, db: AsyncSession) -> Enrollment:
    result = await db.execute(select(Enrollment).where(Enrollment.id == enrollment_id))
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return enrollment


async def _transition(
    db: AsyncSession,
    enrollment: Enrollment,
    new_status: EnrollmentStatus,
    changed_by: Optional[int],
    comment: Optional[str] = None,
) -> None:
    """FSM-переход с записью в журнал."""
    allowed = ENROLLMENT_STATUS_TRANSITIONS.get(enrollment.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Переход '{enrollment.status}' → '{new_status}' запрещён. "
                f"Разрешённые: {[s.value for s in allowed]}"
            ),
        )
    db.add(EnrollmentStatusHistory(
        enrollment_id=enrollment.id,
        from_status=enrollment.status,
        to_status=new_status,
        changed_by=changed_by,
        comment=comment,
    ))
    enrollment.status = new_status


async def _create_student_group_and_invoice(
    db: AsyncSession,
    enrollment: Enrollment,
    group: Group,
    due_days: int,
) -> tuple[StudentGroup, Invoice]:
    """Создаёт StudentGroup и счёт-фактуру Invoice для заявки."""
    # Создаём StudentGroup
    sg = StudentGroup(
        group_id=group.id,
        student_name=enrollment.name,
        student_phone=enrollment.phone,
        student_email=enrollment.email,
        student_type=enrollment.student_type or "adult",
        form_id=enrollment.id,
    )
    db.add(sg)
    await db.flush()  # получаем sg.id

    # Определяем сумму: цена курса за первый месяц
    amount = group.course.price_per_month if group.course else 0

    # Создаём Invoice
    invoice = Invoice(
        group_id=group.id,
        student_group_id=sg.id,
        student_name=enrollment.name,
        amount=amount,
        amount_paid=0,
        period=datetime.utcnow().strftime("%Y-%m"),
        due_date=datetime.utcnow() + timedelta(days=due_days),
        status=PaymentStatus.pending,
        notes=f"Первый месяц обучения. Заявка #{enrollment.id}",
    )
    db.add(invoice)
    await db.flush()  # получаем invoice.id

    return sg, invoice


# ═══════════════════════════════════════════════════════════════════════
# ПУБЛИЧНОЕ API (ДЛЯ ПОСЕТИТЕЛЕЙ САЙТА)
# ═══════════════════════════════════════════════════════════════════════

@router.post("/", response_model=EnrollmentResponse, status_code=201,
             summary="Подача заявки на зачисление")
async def create_enrollment(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Публичный эндпоинт: посетитель сайта оставляет заявку. Статус = pending."""
    enrollment = Enrollment(
        name=data.name,
        phone=data.phone,
        email=data.email,
        comment=data.comment,
        desired_course_id=data.desired_course_id,
        student_type=data.student_type,
        age=data.age,
        source=data.source,
        status=EnrollmentStatus.pending,
    )
    db.add(enrollment)
    await db.flush()

    # Первая запись в историю
    db.add(EnrollmentStatusHistory(
        enrollment_id=enrollment.id,
        from_status=None,
        to_status=EnrollmentStatus.pending,
        changed_by=None,
        comment="Заявка подана через сайт",
    ))
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.get("/my", response_model=List[EnrollmentOut], summary="Мои заявки")
async def get_my_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Пользователь видит свои заявки с историей статусов."""
    result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id)
        .order_by(Enrollment.created_at.desc())
    )
    return result.scalars().all()


# ═══════════════════════════════════════════════════════════════════════
# АДМИНИСТРАТИВНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/admin", response_model=List[EnrollmentListOut], summary="[Админ] Список заявок")
async def admin_list_enrollments(
    status_filter: Optional[EnrollmentStatus] = Query(None, alias="status"),
    course_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Полный список заявок с фильтрами по статусу и курсу. Пагинация."""
    q = select(Enrollment)
    if status_filter:
        q = q.where(Enrollment.status == status_filter)
    if course_id:
        q = q.where(Enrollment.desired_course_id == course_id)
    q = q.order_by(Enrollment.created_at.desc())
    result = await db.execute(q.offset((page - 1) * page_size).limit(page_size))
    return result.scalars().all()


@router.get("/admin/{enrollment_id}", response_model=EnrollmentOut, summary="[Админ] Подробно")
async def admin_get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await _get_enrollment_or_404(enrollment_id, db)


@router.post("/admin/{enrollment_id}/confirm", response_model=EnrollmentOut,
             summary="[Админ] Подтвердить заявку (pending → confirmed)")
async def admin_confirm(
    enrollment_id: int,
    data: EnrollmentConfirm,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Подтверждаем заявку — клиент подходит, готовимся подобрать группу."""
    enrollment = await _get_enrollment_or_404(enrollment_id, db)
    await _transition(db, enrollment, EnrollmentStatus.confirmed, current_user.id, data.comment)
    enrollment.assigned_at = datetime.utcnow()
    enrollment.assigned_by = current_user.id
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/admin/{enrollment_id}/assign-group", response_model=EnrollmentOut,
             summary="[Админ] Зачислить в группу + создать счёт (confirmed → awaiting_payment)")
async def admin_assign_group(
    enrollment_id: int,
    data: EnrollmentAssignGroup,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Действия:
    1. Проверяем, что в группе есть свободные места.
    2. Создаём StudentGroup (запись студента в группу).
    3. Автоматически создаём Invoice с ценой курса и сроком оплаты due_days дней.
    4. Переводим заявку в awaiting_payment.
    """
    enrollment = await _get_enrollment_or_404(enrollment_id, db)

    # 1. Получаем группу с подгрузкой курса (нужен price_per_month)
    from sqlalchemy.orm import selectinload
    g_result = await db.execute(
        select(Group)
        .options(selectinload(Group.course), selectinload(Group.student_groups))
        .where(Group.id == data.group_id)
    )
    group = g_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    # 2. Проверяем наполненность группы
    active_count = sum(1 for sg in group.student_groups if sg.is_active)
    max_students = group.course.max_students if group.course else 8
    if active_count >= max_students:
        raise HTTPException(
            status_code=409,
            detail=f"Группа заполнена ({active_count}/{max_students})"
        )

    # 3-4. Создаём StudentGroup + Invoice
    sg, invoice = await _create_student_group_and_invoice(db, enrollment, group, data.due_days)

    # 5. Обновляем заявку
    enrollment.group_id = group.id
    enrollment.student_group_id = sg.id
    enrollment.invoice_id = invoice.id

    # 6. FSM-переход
    await _transition(
        db, enrollment, EnrollmentStatus.awaiting_payment, current_user.id,
        data.comment or f"Зачислен в группу '{group.name}'. Счёт #{invoice.id} на {invoice.amount} руб."
    )
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/admin/{enrollment_id}/activate", response_model=EnrollmentOut,
             summary="[Админ] Активировать после оплаты (awaiting_payment → active)")
async def admin_activate(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Переводим заявку в active после того, как оплата подтверждена."""
    enrollment = await _get_enrollment_or_404(enrollment_id, db)

    # Проверяем факт оплаты (Invoice.status == paid)
    if enrollment.invoice_id:
        inv_result = await db.execute(select(Invoice).where(Invoice.id == enrollment.invoice_id))
        invoice = inv_result.scalar_one_or_none()
        if invoice and invoice.status != PaymentStatus.paid:
            raise HTTPException(
                status_code=409,
                detail=f"Счёт #{invoice.id} ещё не оплачен (status={invoice.status}). "
                       f"Отметьте оплату в модуле платежей."
            )

    await _transition(db, enrollment, EnrollmentStatus.active, current_user.id, "Оплата подтверждена")
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/admin/{enrollment_id}/reject", response_model=EnrollmentOut,
             summary="[Админ] Отклонить заявку")
async def admin_reject(
    enrollment_id: int,
    data: EnrollmentReject,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Отклоняем заявку — нет свободных мест или не подошёл уровень."""
    enrollment = await _get_enrollment_or_404(enrollment_id, db)
    await _transition(db, enrollment, EnrollmentStatus.rejected, current_user.id, data.reason)
    enrollment.rejection_reason = data.reason
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/admin/{enrollment_id}/cancel", response_model=EnrollmentOut,
             summary="[Админ] Отменить заявку")
async def admin_cancel(
    enrollment_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    enrollment = await _get_enrollment_or_404(enrollment_id, db)
    await _transition(db, enrollment, EnrollmentStatus.cancelled, current_user.id, comment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/admin/{enrollment_id}/withdraw", response_model=EnrollmentOut,
             summary="[Админ] Отчислить студента (active → withdrawn)")
async def admin_withdraw(
    enrollment_id: int,
    data: EnrollmentWithdraw,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Студент отчислен. is_active в StudentGroup становится False."""
    enrollment = await _get_enrollment_or_404(enrollment_id, db)
    await _transition(db, enrollment, EnrollmentStatus.withdrawn, current_user.id, data.reason)

    # Деактивируем StudentGroup
    if enrollment.student_group_id:
        sg_result = await db.execute(
            select(StudentGroup).where(StudentGroup.id == enrollment.student_group_id)
        )
        sg = sg_result.scalar_one_or_none()
        if sg:
            sg.is_active = False

    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.get("/admin/stats/summary", summary="[Админ] Статистика заявок")
async def admin_enrollment_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Количество заявок по каждому статусу — быстрая сводка для админки."""
    rows = await db.execute(
        select(Enrollment.status, func.count(Enrollment.id).label("cnt"))
        .group_by(Enrollment.status)
    )
    stats = {row.status.value: row.cnt for row in rows}
    total = sum(stats.values())
    return {"total": total, "by_status": stats}
