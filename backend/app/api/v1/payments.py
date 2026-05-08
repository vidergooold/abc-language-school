from typing import List
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff, require_student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User
from app.models.payment import Invoice, Payment, PaymentStatus
from app.models.group import Group, Course, StudentGroup
from app.schemas.payment import (
    InvoiceCreate,
    InvoiceOut,
    InvoiceCellStatusUpdate,
    PaymentCreate,
    PaymentOut,
)

router = APIRouter(tags=["Payments"])


# ─── Счета (Invoices) ────────────────────────────────────────────────

@router.get("/invoices", response_model=List[InvoiceOut])
async def get_invoices(
    period: str = Query(None, description="Период, напр. 2026-04"),
    status: PaymentStatus = Query(None),
    group_id: int = Query(None, description="Фильтр по группе"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    query = select(Invoice).order_by(Invoice.due_date)
    if period:
        query = query.where(Invoice.period == period)
    if status:
        query = query.where(Invoice.status == status)
    if group_id is not None:
        query = query.where(Invoice.group_id == group_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/invoices/{invoice_id}/mark-paid", response_model=InvoiceOut)
async def mark_invoice_paid(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Отметить счёт как оплаченный (amount_paid = amount, status = paid)"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    invoice.amount_paid = invoice.amount
    invoice.status = PaymentStatus.paid
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.post("/invoices/cell-status", response_model=InvoiceOut)
async def upsert_invoice_cell_status(
    data: InvoiceCellStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Создать/обновить счёт для ячейки матрицы оплат (студент + период)."""
    result = await db.execute(
        select(Invoice).where(
            and_(
                Invoice.group_id == data.group_id,
                Invoice.student_group_id == data.student_group_id,
                Invoice.period == data.period,
            )
        )
    )
    invoice = result.scalar_one_or_none()

    amount = data.amount
    if amount is None:
        group_result = await db.execute(select(Group).where(Group.id == data.group_id))
        group = group_result.scalar_one_or_none()
        if group:
            course_result = await db.execute(select(Course).where(Course.id == group.course_id))
            course = course_result.scalar_one_or_none()
            amount = Decimal(course.price_per_month) if course else Decimal(0)
        else:
            amount = Decimal(0)

    if not invoice:
        invoice = Invoice(
            group_id=data.group_id,
            student_group_id=data.student_group_id,
            student_name=data.student_name,
            amount=amount,
            amount_paid=Decimal(0),
            period=data.period,
            due_date=datetime.utcnow(),
            status=PaymentStatus.pending,
        )
        db.add(invoice)
        await db.flush()

    invoice.status = data.status
    if data.status == PaymentStatus.paid:
        invoice.amount_paid = invoice.amount
    elif data.status == PaymentStatus.partial:
        invoice.amount_paid = invoice.amount / Decimal(2)
    else:
        invoice.amount_paid = Decimal(0)

    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.post("/invoices", response_model=InvoiceOut)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    invoice = Invoice(**data.model_dump())
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.post("/invoices/bulk")
async def create_bulk_invoices(
    group_id: int,
    period: str,
    due_date: datetime,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Массовое создание счетов для всех активных студентов группы.
    Сумма берётся из цены курса.
    """
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    course_result = await db.execute(select(Course).where(Course.id == group.course_id))
    course = course_result.scalar_one_or_none()

    students_result = await db.execute(
        select(StudentGroup)
        .where(StudentGroup.group_id == group_id, StudentGroup.is_active == True)
    )
    students = students_result.scalars().all()

    created = []
    for student in students:
        # Проверяем, нет ли уже счёта за этот период
        existing = await db.execute(
            select(Invoice).where(
                and_(
                    Invoice.student_group_id == student.id,
                    Invoice.period == period
                )
            )
        )
        if existing.scalar_one_or_none():
            continue  # Счёт уже существует, пропускаем

        invoice = Invoice(
            group_id=group_id,
            student_group_id=student.id,
            student_name=student.student_name,
            amount=Decimal(course.price_per_month) if course else Decimal(0),
            period=period,
            due_date=due_date,
        )
        db.add(invoice)
        created.append(student.student_name)

    await db.commit()
    return {"created": len(created), "students": created}


# ─── Оплаты (Payments) ──────────────────────────────────────────────

@router.get("/payments", response_model=List[PaymentOut])
async def get_payments(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Payment).order_by(Payment.paid_at.desc()))
    return result.scalars().all()


@router.get("/payments/my-summary")
async def get_my_payment_attendance_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    """Объединённый блок оплаты + посещаемости для student/parent аккаунта."""
    student_groups_result = await db.execute(
        select(StudentGroup).where(
            StudentGroup.student_email == current_user.email,
            StudentGroup.is_active == True,
        )
    )
    student_groups = student_groups_result.scalars().all()

    if not student_groups:
        return {
            "student_name": current_user.full_name or current_user.email,
            "student_group_ids": [],
            "total_due": 0.0,
            "total_paid": 0.0,
            "current_debt": 0.0,
            "overpayment": 0.0,
            "cost_per_lesson": 0.0,
            "lessons_attended": 0,
            "lessons_completed": 0,
            "lessons_remaining": 0,
            "lessons_to_next_payment": 0,
            "amount_should_be_paid_now": 0.0,
            "amount_remaining_to_pay_now": 0.0,
            "payment_required": False,
            "payment_reminder": "",
            "next_due_date": None,
        }

    student_group_ids = [sg.id for sg in student_groups]
    group_ids = sorted({sg.group_id for sg in student_groups})

    invoices_result = await db.execute(
        select(Invoice).where(Invoice.student_group_id.in_(student_group_ids))
    )
    invoices = invoices_result.scalars().all()

    total_due = sum((inv.amount or Decimal(0)) for inv in invoices)
    total_paid = sum((inv.amount_paid or Decimal(0)) for inv in invoices)
    debt = total_due - total_paid
    current_debt = max(debt, Decimal(0))
    overpayment = abs(min(debt, Decimal(0)))

    attendance_result = await db.execute(
        select(Attendance.status).where(Attendance.student_group_id.in_(student_group_ids))
    )
    attendance_statuses = [row[0] for row in attendance_result.all()]

    lessons_completed = len(attendance_statuses)
    lessons_attended = sum(
        1
        for st in attendance_statuses
        if st in (AttendanceStatus.present, AttendanceStatus.late, AttendanceStatus.excused)
    )

    total_planned_lessons = Decimal(0)
    if group_ids:
        groups_result = await db.execute(
            select(Group, Course)
            .join(Course, Group.course_id == Course.id)
            .where(Group.id.in_(group_ids))
        )
        for group, course in groups_result.all():
            lessons_per_week = Decimal(course.lessons_per_week or 0)
            duration_months = Decimal(course.duration_months or 0)
            total_planned_lessons += lessons_per_week * duration_months * Decimal(4)

    cost_per_lesson = (total_due / total_planned_lessons) if total_planned_lessons > 0 else Decimal(0)
    amount_should_be_paid_now = min(total_due, cost_per_lesson * Decimal(lessons_completed))
    amount_remaining_to_pay_now = max(amount_should_be_paid_now - total_paid, Decimal(0))

    lessons_remaining = max(int(total_planned_lessons) - lessons_completed, 0)
    lessons_to_next_payment = 0
    if cost_per_lesson > 0 and amount_remaining_to_pay_now > 0:
        lessons_to_next_payment = max(int((amount_remaining_to_pay_now / cost_per_lesson).to_integral_value()), 0)

    now_utc = datetime.utcnow()
    overdue_invoice = next(
        (
            inv for inv in sorted(invoices, key=lambda i: i.due_date)
            if inv.status in (PaymentStatus.pending, PaymentStatus.partial, PaymentStatus.overdue)
            and inv.due_date <= now_utc
        ),
        None,
    )
    next_due_invoice = next(
        (
            inv for inv in sorted(invoices, key=lambda i: i.due_date)
            if inv.status in (PaymentStatus.pending, PaymentStatus.partial, PaymentStatus.overdue)
        ),
        None,
    )

    payment_required = bool(amount_remaining_to_pay_now > 0 or overdue_invoice is not None)
    payment_reminder = "Необходимо оплатить обучение" if payment_required else ""

    return {
        "student_name": student_groups[0].student_name,
        "student_group_ids": student_group_ids,
        "total_due": float(total_due),
        "total_paid": float(total_paid),
        "current_debt": float(current_debt),
        "overpayment": float(overpayment),
        "cost_per_lesson": float(cost_per_lesson),
        "lessons_attended": lessons_attended,
        "lessons_completed": lessons_completed,
        "lessons_remaining": lessons_remaining,
        "lessons_to_next_payment": lessons_to_next_payment,
        "amount_should_be_paid_now": float(amount_should_be_paid_now),
        "amount_remaining_to_pay_now": float(amount_remaining_to_pay_now),
        "payment_required": payment_required,
        "payment_reminder": payment_reminder,
        "next_due_date": next_due_invoice.due_date.isoformat() if next_due_invoice else None,
    }


@router.post("/payments", response_model=PaymentOut)
async def record_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Зафиксировать оплату. Автоматически обновляет статус счёта."""
    payment = Payment(**data.model_dump())
    db.add(payment)

    # Если оплата привязана к счёту — обновляем сумму и статус
    if data.invoice_id:
        inv_result = await db.execute(
            select(Invoice).where(Invoice.id == data.invoice_id)
        )
        invoice = inv_result.scalar_one_or_none()
        if invoice:
            invoice.amount_paid = (invoice.amount_paid or Decimal(0)) + data.amount
            if invoice.amount_paid >= invoice.amount:
                invoice.status = PaymentStatus.paid
            else:
                invoice.status = PaymentStatus.partial

    await db.commit()
    await db.refresh(payment)
    return payment


# ─── Финансовая аналитика ────────────────────────────────────────────

@router.get("/finance/summary")
async def get_finance_summary(
    period: str = Query(None, description="Период, напр. 2026-04"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Финансовая сводка:
    - Начислено (invoiced)
    - Оплачено (collected)
    - Долг (debt)
    - Количество счетов по статусам
    """
    query_filter = Invoice.id > 0
    if period:
        query_filter = and_(query_filter, Invoice.period == period)

    # Итоговые суммы
    total_invoiced = await db.scalar(
        select(func.sum(Invoice.amount)).where(query_filter)
    ) or Decimal(0)

    total_paid = await db.scalar(
        select(func.sum(Invoice.amount_paid)).where(query_filter)
    ) or Decimal(0)

    total_debt = total_invoiced - total_paid

    # Подсчёт по статусам
    statuses = {}
    for status in PaymentStatus:
        count = await db.scalar(
            select(func.count()).select_from(Invoice)
            .where(and_(query_filter, Invoice.status == status))
        )
        statuses[status.value] = count

    # Динамика по месяцам (последние 6 периодов)
    monthly_result = await db.execute(
        select(Invoice.period, func.sum(Invoice.amount), func.sum(Invoice.amount_paid))
        .group_by(Invoice.period)
        .order_by(Invoice.period.desc())
        .limit(6)
    )
    monthly = [
        {"period": row[0], "invoiced": float(row[1] or 0), "paid": float(row[2] or 0)}
        for row in monthly_result.all()
    ]

    return {
        "period": period or "all",
        "total_invoiced": float(total_invoiced),
        "total_paid": float(total_paid),
        "total_debt": float(total_debt),
        "collection_rate": round(float(total_paid / total_invoiced * 100), 1) if total_invoiced > 0 else 0,
        "invoices_by_status": statuses,
        "monthly_trend": monthly,
    }


@router.get("/finance/by-group")
async def get_finance_by_group(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Финансовый отчёт по каждой группе"""
    groups_result = await db.execute(select(Group).order_by(Group.name))
    groups = groups_result.scalars().all()

    report = []
    for group in groups:
        invoiced = await db.scalar(
            select(func.sum(Invoice.amount)).where(Invoice.group_id == group.id)
        ) or Decimal(0)
        paid = await db.scalar(
            select(func.sum(Invoice.amount_paid)).where(Invoice.group_id == group.id)
        ) or Decimal(0)
        students_count = await db.scalar(
            select(func.count()).select_from(StudentGroup)
            .where(StudentGroup.group_id == group.id, StudentGroup.is_active == True)
        )
        report.append({
            "group_id": group.id,
            "group_name": group.name,
            "students_count": students_count,
            "total_invoiced": float(invoiced),
            "total_paid": float(paid),
            "debt": float(invoiced - paid),
        })

    return report
