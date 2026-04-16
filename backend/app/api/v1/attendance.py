"""Посещаемость (router).

Матрица доступа:
  GET  /attendance/my                       — require_student
  POST /attendance/                         — require_staff
  GET  /attendance/lesson/{lesson_id}       — require_staff
  GET  /attendance/student/{id}/stats       — require_staff
  GET  /attendance/group/{group_id}/summary — require_staff
  GET  /attendance/report                   — require_staff (фильтрованный отчёт)
"""
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_student, require_staff
from app.models.attendance import Attendance, AttendanceStatus
from app.models.group import StudentGroup, Group
from app.models.lesson import Lesson
from app.models.user import User
from app.schemas.attendance import AttendanceCreate, AttendanceOut, AttendanceStats

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ─── Студент: своя посещаемость ────────────────────────────────────────────────
@router.get("/my", response_model=List[AttendanceOut])
async def get_my_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    sg_result = await db.execute(
        select(StudentGroup).where(
            and_(
                StudentGroup.student_email == current_user.email,
                StudentGroup.is_active == True,
            )
        )
    )
    student_groups = sg_result.scalars().all()
    if not student_groups:
        return []

    sg_ids = [sg.id for sg in student_groups]
    result = await db.execute(
        select(Attendance)
        .where(Attendance.student_group_id.in_(sg_ids))
        .order_by(Attendance.lesson_date.desc())
    )
    return result.scalars().all()


# ─── Стафф: отметить посещаемость ─────────────────────────────────────────────
@router.post("/", response_model=AttendanceOut)
async def mark_attendance(
    data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    existing = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == data.lesson_id,
                Attendance.student_group_id == data.student_group_id,
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Посещаемость для этого студента на данном занятии уже отмечена"
        )
    record = Attendance(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/lesson/{lesson_id}", response_model=List[AttendanceOut])
async def get_lesson_attendance(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    result = await db.execute(
        select(Attendance).where(Attendance.lesson_id == lesson_id)
    )
    return result.scalars().all()


@router.get("/student/{student_group_id}/stats", response_model=AttendanceStats)
async def get_student_attendance_stats(
    student_group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    student_result = await db.execute(
        select(StudentGroup).where(StudentGroup.id == student_group_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    records_result = await db.execute(
        select(Attendance).where(Attendance.student_group_id == student_group_id)
    )
    records = records_result.scalars().all()
    total   = len(records)
    present = sum(1 for r in records if r.status == AttendanceStatus.present)
    absent  = sum(1 for r in records if r.status == AttendanceStatus.absent)
    late    = sum(1 for r in records if r.status == AttendanceStatus.late)
    excused = sum(1 for r in records if r.status == AttendanceStatus.excused)

    return AttendanceStats(
        student_group_id=student_group_id,
        student_name=student.student_name,
        total_lessons=total,
        present=present,
        absent=absent,
        late=late,
        excused=excused,
        attendance_rate=round(present / total * 100, 1) if total > 0 else 0.0,
    )


@router.get("/group/{group_id}/summary")
async def get_group_attendance_summary(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    students_result = await db.execute(
        select(StudentGroup)
        .where(StudentGroup.group_id == group_id, StudentGroup.is_active == True)
    )
    students = students_result.scalars().all()
    summary = []
    for student in students:
        records_result = await db.execute(
            select(Attendance).where(Attendance.student_group_id == student.id)
        )
        records = records_result.scalars().all()
        total   = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.present)
        summary.append({
            "student_id":   student.id,
            "student_name": student.student_name,
            "total":   total,
            "present": present,
            "rate":    round(present / total * 100, 1) if total > 0 else 0.0,
        })
    return summary


# ─── Отчёт с фильтрами (для страницы посещаемости) ────────────────────────────
@router.get("/report")
async def get_attendance_report(
    branch_id:           Optional[int]  = Query(None),
    teacher_id:          Optional[int]  = Query(None),
    group_id:            Optional[int]  = Query(None),
    date_from:           Optional[date] = Query(None),
    date_to:             Optional[date] = Query(None),
    student_name:        Optional[str]  = Query(None),
    missed_consecutive:  bool           = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """
    Фильтрованный отчёт посещаемости для административного просмотра.
    Параметры:
      branch_id          — фильтр по филиалу
      teacher_id         — фильтр по преподавателю
      group_id           — фильтр по группе
      date_from/date_to  — диапазон дат
      student_name       — поиск по имени студента (ilike)
      missed_consecutive — только пропустившие 2 занятия подряд
    """
    # Базовый запрос: attendance -> student_group -> group -> lesson
    q = (
        select(
            Attendance.id,
            Attendance.lesson_date,
            Attendance.status,
            Attendance.note,
            StudentGroup.student_name,
            StudentGroup.student_email,
            StudentGroup.id.label("student_group_id"),
            Group.id.label("group_id"),
            Group.name.label("group_name"),
            Group.branch_id,
            Group.teacher_id,
            Lesson.id.label("lesson_id"),
        )
        .join(StudentGroup, Attendance.student_group_id == StudentGroup.id)
        .join(Group, StudentGroup.group_id == Group.id)
        .join(Lesson, Attendance.lesson_id == Lesson.id)
    )

    if branch_id:
        q = q.where(Group.branch_id == branch_id)
    if teacher_id:
        q = q.where(Group.teacher_id == teacher_id)
    if group_id:
        q = q.where(Group.id == group_id)
    if date_from:
        dt_from = datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc)
        q = q.where(Attendance.lesson_date >= dt_from)
    if date_to:
        dt_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc)
        q = q.where(Attendance.lesson_date <= dt_to)
    if student_name:
        q = q.where(StudentGroup.student_name.ilike(f"%{student_name}%"))

    q = q.order_by(StudentGroup.student_name, Attendance.lesson_date)
    result = await db.execute(q)
    rows = result.mappings().all()

    records = [dict(r) for r in rows]

    # Фильтр «2 пропуска подряд»
    if missed_consecutive:
        # Группируем записи по student_group_id
        from collections import defaultdict
        by_student: dict = defaultdict(list)
        for rec in records:
            by_student[rec["student_group_id"]].append(rec)

        guilty_ids: set = set()
        for sg_id, recs in by_student.items():
            sorted_recs = sorted(recs, key=lambda r: r["lesson_date"])
            for i in range(len(sorted_recs) - 1):
                if (
                    sorted_recs[i]["status"] == AttendanceStatus.absent
                    and sorted_recs[i + 1]["status"] == AttendanceStatus.absent
                ):
                    guilty_ids.add(sg_id)
                    break

        records = [r for r in records if r["student_group_id"] in guilty_ids]

    # Сериализуем datetime -> str
    for rec in records:
        if isinstance(rec.get("lesson_date"), datetime):
            rec["lesson_date"] = rec["lesson_date"].date().isoformat()

    return records
