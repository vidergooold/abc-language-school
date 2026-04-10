from typing import List
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.payment import Invoice, Payment, PaymentStatus
from app.models.group import Group, Course, StudentGroup
from app.schemas.payment import InvoiceCreate, InvoiceOut, PaymentCreate, PaymentOut

router = APIRouter(tags=["Payments"])


# ─── Счета (Invoices) ────────────────────────────────────────────────

@router.get("/invoices", response_model=List[InvoiceOut])
async def get_invoices(
    period: str = Query(None, description="Период, напр. 2026-04"),
    status: PaymentStatus = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    query = select(Invoice).order_by(Invoice.due_date)
    if period:
        query = query.where(Invoice.period == period)
    if status:
        query = query.where(Invoice.status == status)
    result = await db.execute(query)
    return result.scalars().all()


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
