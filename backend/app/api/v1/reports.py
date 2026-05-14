import hashlib, json
import csv
import io
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
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
MAX_PDF_ROWS = 200
MAX_PDF_LINE_LENGTH = 1200


def _make_hash(params: dict) -> str:
    return hashlib.md5(json.dumps(params, sort_keys=True, default=str).encode()).hexdigest()


def _rows_from_data(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("items"), list):
            return data["items"]
        return [data]
    return []


def _period_bounds(period: str):
    try:
        year, month = period.split("-")
        year_int = int(year)
        month_int = int(month)
        if month_int < 1 or month_int > 12:
            raise ValueError("month out of range")
    except Exception:
        raise HTTPException(status_code=400, detail="period должен быть в формате YYYY-MM")
    start = datetime(year_int, month_int, 1)
    end = datetime(year_int + (1 if month_int == 12 else 0), 1 if month_int == 12 else month_int + 1, 1)
    return start, end


def _to_csv_bytes(rows: list[dict]) -> bytes:
    output = io.StringIO()
    if not rows:
        output.write("no_data\n")
    else:
        headers = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in headers})
    return output.getvalue().encode("utf-8")


def _to_simple_pdf_bytes(title: str, rows: list[dict]) -> bytes:
    """Generate a minimal text-only PDF for report export from row dictionaries."""
    lines = [title, ""]
    if not rows:
        lines.append("No data")
    else:
        for row in rows[:MAX_PDF_ROWS]:
            line = "; ".join(f"{k}: {row.get(k)}" for k in sorted(row.keys()))
            lines.append(line[:MAX_PDF_LINE_LENGTH] + ("…" if len(line) > MAX_PDF_LINE_LENGTH else ""))
        if len(rows) > MAX_PDF_ROWS:
            lines.append(f"... truncated: showing first {MAX_PDF_ROWS} of {len(rows)} rows")

    text_parts = []
    for line in lines:
        safe = (
            str(line)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("\r", " ")
            .replace("\n", " ")
            .replace("\t", " ")
        )
        text_parts.append(f"({safe}) Tj")
        text_parts.append("T*")
    content = "BT /F1 10 Tf 50 790 Td " + " ".join(text_parts) + " ET"
    # PDF text stream in this lightweight implementation uses latin-1; unsupported chars are replaced.
    content_bytes = content.encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(f"5 0 obj << /Length {len(content_bytes)} >> stream\n".encode("ascii") + content_bytes + b"\nendstream endobj\n")

    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(pdf.tell())
        pdf.write(obj)
    xref_pos = pdf.tell()
    pdf.write(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.write(f"{off:010d} 00000 n \n".encode("ascii"))
    pdf.write(f"trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("ascii"))
    return pdf.getvalue()


def _export_response(report_name: str, data, export_format: str):
    rows = _rows_from_data(data)
    if export_format == "excel":
        return Response(
            content=_to_csv_bytes(rows),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{report_name}.csv"'},
        )
    if export_format == "pdf":
        return Response(
            content=_to_simple_pdf_bytes(report_name, rows),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{report_name}.pdf"'},
        )
    return {"data": data}


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
    teacher_id: int = Query(None),
    student_name: str = Query(None),
    export_format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Отчёт по посещаемости.
    Для каждой группы: всего занятий, посещено, пропущено, % посещаемости.
    Кэшируется на 30 минут.
    """
    params = {
        "period": period,
        "group_id": group_id,
        "teacher_id": teacher_id,
        "student_name": student_name,
    }

    async def build():
        async def _attendance_count(lesson_ids, status: AttendanceStatus | None = None):
            base = (
                select(func.count())
                .select_from(Attendance)
                .join(StudentGroup, StudentGroup.id == Attendance.student_group_id)
                .where(Attendance.lesson_id.in_(lesson_ids))
            )
            if status is not None:
                base = base.where(Attendance.status == status)
            if student_name:
                base = base.where(StudentGroup.student_name.ilike(f"%{student_name}%"))
            return (await db.scalar(base)) or 0

        groups_q = select(Group)
        if group_id:
            groups_q = groups_q.where(Group.id == group_id)
        groups_result = await db.execute(groups_q)
        groups = groups_result.scalars().all()

        rows = []
        for group in groups:
            lesson_q = select(Lesson).where(Lesson.group_id == group.id)
            if teacher_id:
                lesson_q = lesson_q.where(Lesson.teacher_id == teacher_id)
            if period:
                # фильтр по периоду через lesson_date
                start, end = _period_bounds(period)
                lesson_q = lesson_q.where(
                    and_(Lesson.lesson_date >= start, Lesson.lesson_date < end)
                )
            lessons_result = await db.execute(lesson_q)
            lessons = lessons_result.scalars().all()
            lesson_ids = [l.id for l in lessons]

            if not lesson_ids:
                continue

            total_att = await _attendance_count(lesson_ids, None)
            present = await _attendance_count(lesson_ids, AttendanceStatus.present)
            absent = await _attendance_count(lesson_ids, AttendanceStatus.absent)
            excused = await _attendance_count(lesson_ids, AttendanceStatus.excused)

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

    payload = await _get_or_build(db, "attendance", params, build)
    if export_format in ("excel", "pdf"):
        return _export_response("attendance-report", payload["data"], export_format)
    return payload


@router.get("/teacher-load")
async def report_teacher_load(
    period: str = Query(None, description="YYYY-MM, напр. 2026-04"),
    teacher_id: int = Query(None),
    group_id: int = Query(None),
    export_format: str = Query("json"),
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
    params = {"type": "teacher_load", "period": period, "teacher_id": teacher_id, "group_id": group_id}

    async def build():
        teachers_query = select(Teacher).where(Teacher.is_active == True)
        if teacher_id:
            teachers_query = teachers_query.where(Teacher.id == teacher_id)
        teachers_result = await db.execute(teachers_query)
        teachers = teachers_result.scalars().all()
        rows = []
        for t in teachers:
            lessons_query = select(Lesson).where(and_(
                Lesson.teacher_id == t.id,
                Lesson.status == LessonStatus.scheduled,
            ))
            if group_id:
                lessons_query = lessons_query.where(Lesson.group_id == group_id)
            if period:
                start, end = _period_bounds(period)
                lessons_query = lessons_query.where(and_(Lesson.lesson_date >= start, Lesson.lesson_date < end))
            lessons_result = await db.execute(lessons_query)
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

    payload = await _get_or_build(db, "teacher_load", params, build, ttl_minutes=15)
    if export_format in ("excel", "pdf"):
        return _export_response("teacher-workload-report", payload["data"], export_format)
    return payload


@router.get("/financial")
async def report_financial(
    period: str = Query(None, description="YYYY-MM, напр. 2026-04"),
    group_id: int = Query(None),
    teacher_id: int = Query(None),
    student_name: str = Query(None),
    export_format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    query = select(Invoice).order_by(Invoice.due_date.desc())
    if period:
        query = query.where(Invoice.period == period)
    if group_id:
        query = query.where(Invoice.group_id == group_id)
    if student_name:
        query = query.where(Invoice.student_name.ilike(f"%{student_name}%"))
    if teacher_id:
        query = query.join(Group, Group.id == Invoice.group_id).where(Group.teacher_id == teacher_id)

    invoices = (await db.execute(query)).scalars().all()
    rows = []
    for inv in invoices:
        rows.append({
            "invoice_id": inv.id,
            "student_name": inv.student_name,
            "group_id": inv.group_id,
            "period": inv.period,
            "amount": float(inv.amount or 0),
            "amount_paid": float(inv.amount_paid or 0),
            "debt": float((inv.amount or Decimal(0)) - (inv.amount_paid or Decimal(0))),
            "status": inv.status.value if hasattr(inv.status, "value") else str(inv.status),
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
        })
    total_amount = sum(r["amount"] for r in rows)
    total_paid = sum(r["amount_paid"] for r in rows)
    data = {
        "total_invoiced": round(total_amount, 2),
        "total_paid": round(total_paid, 2),
        "total_debt": round(total_amount - total_paid, 2),
        "items": rows,
    }
    if export_format in ("excel", "pdf"):
        return _export_response("financial-report", data, export_format)
    return data


@router.get("/lessons-conducted")
async def report_lessons_conducted(
    period: str = Query(None, description="YYYY-MM, напр. 2026-04"),
    group_id: int = Query(None),
    teacher_id: int = Query(None),
    student_name: str = Query(None),
    export_format: str = Query("json"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    lessons_query = select(Lesson).where(Lesson.status.in_([LessonStatus.completed, LessonStatus.rescheduled]))
    if group_id:
        lessons_query = lessons_query.where(Lesson.group_id == group_id)
    if teacher_id:
        lessons_query = lessons_query.where(Lesson.teacher_id == teacher_id)
    if period:
        start, end = _period_bounds(period)
        lessons_query = lessons_query.where(and_(Lesson.lesson_date >= start, Lesson.lesson_date < end))
    if student_name:
        lessons_query = lessons_query.join(StudentGroup, StudentGroup.group_id == Lesson.group_id).where(
            StudentGroup.student_name.ilike(f"%{student_name}%")
        )

    lessons_result = await db.execute(lessons_query)
    lessons = lessons_result.scalars().all()
    rows = [{
        "lesson_id": lesson.id,
        "group_id": lesson.group_id,
        "teacher_id": lesson.teacher_id,
        "lesson_date": lesson.lesson_date.isoformat() if lesson.lesson_date else None,
        "status": lesson.status.value if hasattr(lesson.status, "value") else str(lesson.status),
        "topic": lesson.topic or "",
    } for lesson in lessons]
    data = {"count": len(rows), "items": rows}
    if export_format in ("excel", "pdf"):
        return _export_response("lessons-conducted-report", data, export_format)
    return data


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
