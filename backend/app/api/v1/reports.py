import hashlib, json
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.report import ReportCache
from app.models.attendance import Attendance, AttendanceStatus
from app.models.schedule import Lesson, LessonStatus
from app.models.group import Group, StudentGroup, Course
from app.models.payment import Invoice, Payment, PaymentStatus
from app.models.teacher import Teacher

router = APIRouter(prefix="/reports", tags=["Reports"])


def _make_hash(params: dict) -> str:
    return hashlib.md5(json.dumps(params, sort_keys=True, default=str).encode()).hexdigest()


async def _get_or_build(
    db: AsyncSession,
    report_type: str,
    params: dict,
    builder,
    ttl_minutes: int = 30,
):
    """Читает из кэша или строит отчёт и кэширует."""
    h = _make_hash(params)
    cached = await db.scalar(
        select(ReportCache).where(
            and_(
                ReportCache.report_type == report_type,
                ReportCache.params_hash == h,
                ReportCache.expires_at > datetime.utcnow(),
            )
        )
    )
    if cached:
        return {"from_cache": True, "generated_at": cached.generated_at, "data": cached.data}

    data = await builder()
    cache_entry = ReportCache(
        report_type=report_type,
        params_hash=h,
        period=params.get("period"),
        data=data,
        expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
    )
    db.add(cache_entry)
    await db.commit()
    return {"from_cache": False, "generated_at": datetime.utcnow(), "data": data}


@router.get("/attendance")
async def report_attendance(
    period: str = Query(None, description="YYYY-MM, напр. 2026-04"),
    group_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Отчёт по посещаемости.
    Для каждой группы: всего занятий, посещено, пропущено, % посещаемости.
    Кэшируется на 30 минут.
    """
    params = {"period": period, "group_id": group_id}

    async def build():
        groups_q = select(Group)
        if group_id:
            groups_q = groups_q.where(Group.id == group_id)
        groups_result = await db.execute(groups_q)
        groups = groups_result.scalars().all()

        rows = []
        for group in groups:
            lesson_q = select(Lesson).where(Lesson.group_id == group.id)
            if period:
                # фильтр по периоду через lesson_date
                year, month = period.split("-")
                from datetime import date
                start = datetime(int(year), int(month), 1)
                if int(month) == 12:
                    end = datetime(int(year) + 1, 1, 1)
                else:
                    end = datetime(int(year), int(month) + 1, 1)
                lesson_q = lesson_q.where(
                    and_(Lesson.lesson_date >= start, Lesson.lesson_date < end)
                )
            lessons_result = await db.execute(lesson_q)
            lessons = lessons_result.scalars().all()
            lesson_ids = [l.id for l in lessons]

            if not lesson_ids:
                continue

            total_att = await db.scalar(
                select(func.count()).select_from(Attendance)
                .where(Attendance.lesson_id.in_(lesson_ids))
            ) or 0
            present = await db.scalar(
                select(func.count()).select_from(Attendance)
                .where(and_(
                    Attendance.lesson_id.in_(lesson_ids),
                    Attendance.status == AttendanceStatus.present,
                ))
            ) or 0
            absent = await db.scalar(
                select(func.count()).select_from(Attendance)
                .where(and_(
                    Attendance.lesson_id.in_(lesson_ids),
                    Attendance.status == AttendanceStatus.absent,
                ))
            ) or 0
            excused = await db.scalar(
                select(func.count()).select_from(Attendance)
                .where(and_(
                    Attendance.lesson_id.in_(lesson_ids),
                    Attendance.status == AttendanceStatus.excused,
                ))
            ) or 0

            rows.append({
                "group_id":    group.id,
                "group_name":  group.name,
                "lessons_count": len(lessons),
                "total_records": total_att,
                "present":     present,
                "absent":      absent,
                "excused":     excused,
                "attendance_pct": round(present / total_att * 100, 1) if total_att > 0 else 0,
            })
        return rows

    return await _get_or_build(db, "attendance", params, build)


@router.get("/teacher-load")
async def report_teacher_load(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Отчёт по загрузке преподавателей:
    - Часов в неделю
    - Количество групп
    - Средняя заполненность групп
    Кэшируется на 15 минут.
    """
    params = {"type": "teacher_load"}

    async def build():
        teachers_result = await db.execute(select(Teacher).where(Teacher.is_active == True))
        teachers = teachers_result.scalars().all()
        rows = []
        for t in teachers:
            lessons_result = await db.execute(
                select(Lesson).where(and_(
                    Lesson.teacher_id == t.id,
                    Lesson.status == LessonStatus.scheduled,
                ))
            )
            lessons = lessons_result.scalars().all()
            hours_per_week = sum(
                (datetime.combine(datetime.today(), l.time_end) -
                 datetime.combine(datetime.today(), l.time_start)).seconds / 3600
                for l in lessons
            )
            group_ids = list({l.group_id for l in lessons})
            total_students = 0
            for gid in group_ids:
                cnt = await db.scalar(
                    select(func.count()).select_from(StudentGroup)
                    .where(and_(StudentGroup.group_id == gid, StudentGroup.is_active == True))
                ) or 0
                total_students += cnt
            rows.append({
                "teacher_id":      t.id,
                "teacher_name":    t.full_name,
                "lessons_per_week": len(lessons),
                "hours_per_week":  round(hours_per_week, 1),
                "groups_count":    len(group_ids),
                "students_total":  total_students,
            })
        return sorted(rows, key=lambda x: x["hours_per_week"], reverse=True)

    return await _get_or_build(db, "teacher_load", params, build, ttl_minutes=15)


@router.get("/debts")
async def report_debts(
    period: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Отчёт по задолженностям:
    - Список студентов с долгом > 0
    - Сумма долга, просроченные счета
    """
    query = select(Invoice).where(
        Invoice.status.in_([PaymentStatus.pending, PaymentStatus.partial, PaymentStatus.overdue])
    )
    if period:
        query = query.where(Invoice.period == period)
    result = await db.execute(query.order_by(Invoice.due_date))
    invoices = result.scalars().all()

    rows = []
    for inv in invoices:
        debt = float(inv.amount) - float(inv.amount_paid or 0)
        if debt <= 0:
            continue
        rows.append({
            "invoice_id":   inv.id,
            "student_name": inv.student_name,
            "period":       inv.period,
            "amount":       float(inv.amount),
            "amount_paid":  float(inv.amount_paid or 0),
            "debt":         round(debt, 2),
            "status":       inv.status.value,
            "due_date":     inv.due_date.isoformat() if inv.due_date else None,
            "overdue":      inv.due_date < datetime.utcnow() if inv.due_date else False,
        })
    total_debt = sum(r["debt"] for r in rows)
    return {"total_debt": round(total_debt, 2), "count": len(rows), "items": rows}


@router.get("/monthly-revenue")
async def report_monthly_revenue(
    months: int = Query(12, ge=1, le=36),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Ежемесячная динамика выручки за последние N месяцев:
    - Начислено, оплачено, долг, число активных студентов.
    """
    result = await db.execute(
        select(
            Invoice.period,
            func.sum(Invoice.amount).label("invoiced"),
            func.sum(Invoice.amount_paid).label("paid"),
            func.count(Invoice.id).label("invoices_count"),
        )
        .group_by(Invoice.period)
        .order_by(Invoice.period.desc())
        .limit(months)
    )
    rows = []
    for row in result.all():
        invoiced = float(row.invoiced or 0)
        paid     = float(row.paid or 0)
        rows.append({
            "period":         row.period,
            "invoiced":       invoiced,
            "paid":           paid,
            "debt":           round(invoiced - paid, 2),
            "invoices_count": row.invoices_count,
            "collection_rate": round(paid / invoiced * 100, 1) if invoiced > 0 else 0,
        })
    return list(reversed(rows))  # хронологический порядок


@router.delete("/cache")
async def clear_report_cache(
    report_type: str = Query(None, description="Тип отчёта или all для очистки всего"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Очистить кэш отчётов (вручную или перед перегенерацией)."""
    from sqlalchemy import delete
    if report_type and report_type != "all":
        await db.execute(delete(ReportCache).where(ReportCache.report_type == report_type))
    else:
        await db.execute(delete(ReportCache))
    await db.commit()
    return {"ok": True, "cleared": report_type or "all"}
