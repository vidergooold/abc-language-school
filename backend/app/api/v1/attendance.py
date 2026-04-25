"""Посещаемость (router).

Матрица доступа:
  GET  /attendance/my                       — require_student
  POST /attendance/                         — require_staff
  GET  /attendance/lesson/{lesson_id}       — require_staff
  GET  /attendance/student/{id}/stats       — require_staff
  GET  /attendance/group/{group_id}/summary — require_staff
  GET  /attendance/report                   — require_staff (фильтрованный отчёт)
"""
from datetime import date, datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_student, require_staff
from app.models.attendance import Attendance, AttendanceStatus
from app.models.group import StudentGroup, Group, Course
from app.models.schedule import DayOfWeek, Lesson, LessonStatus
from app.models.homework import Homework
from app.models.payment import Invoice
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.attendance import AttendanceCreate, AttendanceOut, AttendanceStats, AttendanceUpsert

router = APIRouter(prefix="/attendance", tags=["Attendance"])


class MatrixDateCreate(BaseModel):
    lesson_date: date


class MatrixSlotUpdate(BaseModel):
    lesson_id: int
    old_date: date
    new_date: date


class MatrixSlotDelete(BaseModel):
    lesson_id: int
    slot_date: date


class MaterialTopicUpdate(BaseModel):
    lesson_id: int
    topic: str


_DOW_BY_WEEKDAY_INDEX = {
    0: DayOfWeek.monday,
    1: DayOfWeek.tuesday,
    2: DayOfWeek.wednesday,
    3: DayOfWeek.thursday,
    4: DayOfWeek.friday,
    5: DayOfWeek.saturday,
    6: DayOfWeek.sunday,
}


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


@router.put("/upsert", response_model=AttendanceOut)
async def upsert_attendance(
    data: AttendanceUpsert,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_staff),
):
    lesson_result = await db.execute(select(Lesson).where(Lesson.id == data.lesson_id))
    lesson = lesson_result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    student_result = await db.execute(
        select(StudentGroup).where(
            and_(
                StudentGroup.id == data.student_group_id,
                StudentGroup.is_active == True,
            )
        )
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент группы не найден")

    if lesson.group_id != student.group_id:
        raise HTTPException(status_code=400, detail="Студент не относится к группе выбранного занятия")

    # For specific lessons use the lesson's own date; for recurring ones use the date from the request
    if lesson.lesson_date is not None:
        lesson_dt = lesson.lesson_date
    else:
        if data.lesson_date is None:
            raise HTTPException(status_code=400, detail="lesson_date обязателен для повторяющихся занятий")
        lesson_dt = data.lesson_date

    existing_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == data.lesson_id,
                Attendance.student_group_id == data.student_group_id,
                Attendance.lesson_date == lesson_dt,
            )
        )
    )
    record = existing_result.scalar_one_or_none()

    if record:
        record.status = data.status
        record.grade = data.grade
        record.note = data.note
        record.lesson_date = lesson_dt
    else:
        record = Attendance(
            lesson_id=data.lesson_id,
            student_group_id=data.student_group_id,
            status=data.status,
            grade=data.grade,
            note=data.note,
            lesson_date=lesson_dt,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record


@router.get("/group/{group_id}/matrix")
async def get_group_attendance_matrix(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    students_result = await db.execute(
        select(StudentGroup)
        .where(
            and_(
                StudentGroup.group_id == group_id,
                StudentGroup.is_active == True,
            )
        )
        .order_by(StudentGroup.student_name)
    )
    students = students_result.scalars().all()

    # Fetch all active lessons for the group (both specific-dated and recurring)
    lessons_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.status.in_([
                    LessonStatus.scheduled,
                    LessonStatus.rescheduled,
                    LessonStatus.completed,
                ]),
            )
        )
    )
    lessons = lessons_result.scalars().all()

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    _DOW_TO_WEEKDAY = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
    }

    lesson_slots: list[dict] = []
    for lesson in lessons:
        if lesson.lesson_date is not None:
            # Specific one-time lesson — check if it falls in range
            ld = lesson.lesson_date
            ld_date = ld.date() if isinstance(ld, datetime) else ld
            if effective_from <= ld_date <= effective_to:
                lesson_slots.append({
                    "id": lesson.id,
                    "slot_date": ld_date.isoformat(),
                    "time_start": lesson.time_start.isoformat() if lesson.time_start else None,
                    "is_custom_date": True,
                })
        elif lesson.day_of_week is not None:
            # Recurring lesson — generate one slot per week in range
            dow_raw = lesson.day_of_week
            dow_str = dow_raw.value if hasattr(dow_raw, 'value') else str(dow_raw)
            dow = _DOW_TO_WEEKDAY.get(dow_str.lower(), -1)
            if dow == -1:
                continue
            current = effective_from
            while current.weekday() != dow:
                current += timedelta(days=1)
            while current <= effective_to:
                lesson_slots.append({
                    "id": lesson.id,
                    "slot_date": current.isoformat(),
                    "time_start": lesson.time_start.isoformat() if lesson.time_start else None,
                    "is_custom_date": False,
                })
                current += timedelta(days=7)

    # Sort by date then time; deduplicate same lesson on same date
    lesson_slots.sort(key=lambda x: (x["slot_date"], x["time_start"] or ""))
    seen_slots: set[str] = set()
    unique_slots: list[dict] = []
    for slot in lesson_slots:
        k = f"{slot['id']}:{slot['slot_date']}"
        if k not in seen_slots:
            seen_slots.add(k)
            unique_slots.append(slot)
    lesson_slots = unique_slots

    lesson_ids = list({slot["id"] for slot in lesson_slots})
    student_ids = [student.id for student in students]

    records = []
    if lesson_ids and student_ids:
        records_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.lesson_id.in_(lesson_ids),
                    Attendance.student_group_id.in_(student_ids),
                )
            )
        )
        records = records_result.scalars().all()

    return {
        "students": [
            {
                "id": s.id,
                "student_name": s.student_name,
                "student_email": s.student_email,
            }
            for s in students
        ],
        "lessons": lesson_slots,
        "records": [
            {
                "id": r.id,
                "lesson_id": r.lesson_id,
                "student_group_id": r.student_group_id,
                "status": r.status,
                "note": r.note,
                # Return only the date part so it matches slot_date on the frontend
                "lesson_date": r.lesson_date.date().isoformat() if r.lesson_date else None,
            }
            for r in records
        ],
    }


@router.post("/group/{group_id}/matrix/add-date")
async def add_group_matrix_date(
    group_id: int,
    payload: MatrixDateCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    weekday_enum = _DOW_BY_WEEKDAY_INDEX[payload.lesson_date.weekday()]

    active_statuses = [
        LessonStatus.scheduled,
        LessonStatus.rescheduled,
        LessonStatus.completed,
    ]

    template_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.lesson_date.is_(None),
                Lesson.day_of_week == weekday_enum,
                Lesson.status.in_(active_statuses),
            )
        )
        .order_by(Lesson.time_start.asc())
    )
    template = template_result.scalars().first()

    if template is None:
        fallback_result = await db.execute(
            select(Lesson)
            .where(
                and_(
                    Lesson.group_id == group_id,
                    Lesson.status.in_(active_statuses),
                )
            )
            .order_by(Lesson.time_start.asc())
        )
        template = fallback_result.scalars().first()

    if template is None:
        raise HTTPException(status_code=400, detail="Для группы нет шаблона занятия")

    duplicate_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.group_id == group_id,
                func.date(Lesson.lesson_date) == payload.lesson_date,
                Lesson.time_start == template.time_start,
                Lesson.time_end == template.time_end,
                Lesson.status.in_(active_statuses),
            )
        )
    )
    duplicate = duplicate_result.scalar_one_or_none()
    if duplicate is not None:
        raise HTTPException(status_code=400, detail="Эта дата уже добавлена")

    new_lesson = Lesson(
        group_id=group_id,
        teacher_id=template.teacher_id,
        classroom_id=template.classroom_id,
        branch_id=template.branch_id,
        program_id=template.program_id,
        day_of_week=weekday_enum,
        time_start=template.time_start,
        time_end=template.time_end,
        topic=template.topic,
        status=LessonStatus.scheduled,
        lesson_date=datetime.combine(payload.lesson_date, datetime.min.time()),
        is_recurring=False,
    )
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)

    return {
        "id": new_lesson.id,
        "slot_date": payload.lesson_date.isoformat(),
        "time_start": new_lesson.time_start.isoformat() if new_lesson.time_start else None,
    }


@router.put("/group/{group_id}/matrix/update-date")
async def update_group_matrix_date(
    group_id: int,
    payload: MatrixSlotUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    lesson_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.id == payload.lesson_id,
                Lesson.group_id == group_id,
                Lesson.is_recurring == False,
                Lesson.lesson_date.is_not(None),
                func.date(Lesson.lesson_date) == payload.old_date,
            )
        )
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Дата занятия для редактирования не найдена")

    weekday_enum = _DOW_BY_WEEKDAY_INDEX[payload.new_date.weekday()]

    duplicate_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.group_id == group_id,
                Lesson.id != lesson.id,
                func.date(Lesson.lesson_date) == payload.new_date,
                Lesson.time_start == lesson.time_start,
                Lesson.time_end == lesson.time_end,
                Lesson.status.in_([
                    LessonStatus.scheduled,
                    LessonStatus.rescheduled,
                    LessonStatus.completed,
                ]),
            )
        )
    )
    if duplicate_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="На эту дату уже есть занятие с тем же временем")

    lesson.lesson_date = datetime.combine(payload.new_date, datetime.min.time())
    lesson.day_of_week = weekday_enum

    attendance_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == lesson.id,
                func.date(Attendance.lesson_date) == payload.old_date,
            )
        )
    )
    attendance_rows = attendance_result.scalars().all()
    for row in attendance_rows:
        row.lesson_date = datetime.combine(payload.new_date, datetime.min.time())

    await db.commit()

    return {
        "id": lesson.id,
        "slot_date": payload.new_date.isoformat(),
    }


@router.delete("/group/{group_id}/matrix/delete-date")
async def delete_group_matrix_date(
    group_id: int,
    payload: MatrixSlotDelete,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    lesson_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.id == payload.lesson_id,
                Lesson.group_id == group_id,
                Lesson.is_recurring == False,
                Lesson.lesson_date.is_not(None),
                func.date(Lesson.lesson_date) == payload.slot_date,
            )
        )
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Дата занятия для удаления не найдена")

    attendance_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == lesson.id,
                func.date(Attendance.lesson_date) == payload.slot_date,
            )
        )
    )
    attendance_rows = attendance_result.scalars().all()
    for row in attendance_rows:
        await db.delete(row)

    await db.delete(lesson)
    await db.commit()

    return {"ok": True}


@router.get("/group/{group_id}/materials-matrix")
async def get_group_materials_matrix(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    if group_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    lessons_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.lesson_date.is_not(None),
                func.date(Lesson.lesson_date) >= effective_from,
                func.date(Lesson.lesson_date) <= effective_to,
                Lesson.status.in_([
                    LessonStatus.scheduled,
                    LessonStatus.rescheduled,
                    LessonStatus.completed,
                ]),
            )
        )
        .order_by(Lesson.lesson_date.asc(), Lesson.time_start.asc())
    )
    lessons = lessons_result.scalars().all()

    slots = []
    for lesson in lessons:
        ld = lesson.lesson_date.date() if isinstance(lesson.lesson_date, datetime) else lesson.lesson_date
        slots.append({
            "id": lesson.id,
            "slot_date": ld.isoformat(),
            "time_start": lesson.time_start.isoformat() if lesson.time_start else None,
            "topic": lesson.topic or "",
            "is_custom_date": True,
        })

    return {"slots": slots}


@router.put("/group/{group_id}/materials/update-topic")
async def update_group_material_topic(
    group_id: int,
    payload: MaterialTopicUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    lesson_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.id == payload.lesson_id,
                Lesson.group_id == group_id,
                Lesson.lesson_date.is_not(None),
            )
        )
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    lesson.topic = payload.topic.strip()
    await db.commit()

    return {
        "id": lesson.id,
        "topic": lesson.topic or "",
    }


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
            Lesson.branch_id,
            Lesson.teacher_id,
            Lesson.id.label("lesson_id"),
        )
        .join(StudentGroup, Attendance.student_group_id == StudentGroup.id)
        .join(Group, StudentGroup.group_id == Group.id)
        .join(Lesson, Attendance.lesson_id == Lesson.id)
    )

    if branch_id:
        q = q.where(Lesson.branch_id == branch_id)
    if teacher_id:
        q = q.where(Lesson.teacher_id == teacher_id)
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

        def _status_to_str(value) -> str:
            if hasattr(value, "value"):
                return str(value.value).lower()
            return str(value).lower()

        by_student: dict = defaultdict(list)
        for rec in records:
            by_student[rec["student_group_id"]].append(rec)

        guilty_ids: set = set()
        for sg_id, recs in by_student.items():
            sorted_recs = sorted(recs, key=lambda r: r["lesson_date"])
            for i in range(len(sorted_recs) - 1):
                curr_status = _status_to_str(sorted_recs[i]["status"])
                next_status = _status_to_str(sorted_recs[i + 1]["status"])
                if (
                    curr_status == AttendanceStatus.absent.value
                    and next_status == AttendanceStatus.absent.value
                ):
                    guilty_ids.add(sg_id)
                    break

        records = [r for r in records if r["student_group_id"] in guilty_ids]

    # Сериализуем datetime -> str
    for rec in records:
        if isinstance(rec.get("lesson_date"), datetime):
            rec["lesson_date"] = rec["lesson_date"].date().isoformat()

    return records


# ─── Вкладка: Материал урока ──────────────────────────────────────────────────
@router.get("/group/{group_id}/materials")
async def get_group_materials(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """
    Список материалов (тем) уроков для группы в указанном периоде.
    """
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Группа не найдена")

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    dt_from = datetime(effective_from.year, effective_from.month, effective_from.day, tzinfo=timezone.utc)
    dt_to = datetime(effective_to.year, effective_to.month, effective_to.day, 23, 59, 59, tzinfo=timezone.utc)

    materials_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.topic.isnot(None),
                Lesson.status.in_([LessonStatus.scheduled, LessonStatus.completed, LessonStatus.rescheduled]),
            )
        )
        .order_by(Lesson.lesson_date.desc() if Lesson.lesson_date else Lesson.day_of_week)
    )
    lessons = materials_result.scalars().all()

    materials = []
    for lesson in lessons:
        if lesson.lesson_date:
            ld = lesson.lesson_date.date() if isinstance(lesson.lesson_date, datetime) else lesson.lesson_date
            if dt_from.date() <= ld <= dt_to.date():
                materials.append({
                    "id": lesson.id,
                    "lesson_date": ld.isoformat(),
                    "topic": lesson.topic,
                    "description": lesson.topic or "",  # Use topic as description for now
                })

    return materials


# ─── Вкладка: Домашнее задание ─────────────────────────────────────────────
@router.get("/group/{group_id}/homeworks")
async def get_group_homeworks(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """
    Список домашних заданий для группы в указанном периоде.
    """
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Группа не найдена")

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    dt_from = datetime(effective_from.year, effective_from.month, effective_from.day, tzinfo=timezone.utc)
    dt_to = datetime(effective_to.year, effective_to.month, effective_to.day, 23, 59, 59, tzinfo=timezone.utc)

    homeworks_result = await db.execute(
        select(Homework)
        .where(
            and_(
                Homework.group_id == group_id,
                Homework.due_date >= dt_from,
                Homework.due_date <= dt_to,
            )
        )
        .order_by(Homework.due_date.desc())
    )
    homeworks = homeworks_result.scalars().all()

    return [
        {
            "id": hw.id,
            "title": hw.title,
            "description": hw.description or hw.title,
            "created_at": hw.created_at.isoformat() if hw.created_at else None,
            "deadline": hw.due_date.isoformat() if hw.due_date else None,
        }
        for hw in homeworks
    ]


# ─── Вкладка: Оплата обучения ──────────────────────────────────────────────
@router.get("/group/{group_id}/payments")
async def get_group_payments(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """
    Матрица платежей: студенты × месяцы с статусом оплаты.
    """
    group_result = await db.execute(
        select(StudentGroup)
        .where(
            and_(
                StudentGroup.group_id == group_id,
                StudentGroup.is_active == True,
            )
        )
        .order_by(StudentGroup.student_name)
    )
    students = group_result.scalars().all()

    effective_from = date_from or (date.today() - timedelta(days=90))
    effective_to = date_to or date.today()

    # Get all invoices for these students in the date range
    student_ids = [s.id for s in students]
    if not student_ids:
        return {
            "students": [],
            "months": [],
            "records": {},
        }

    invoices_result = await db.execute(
        select(Invoice)
        .where(
            and_(
                Invoice.student_group_id.in_(student_ids),
            )
        )
    )
    invoices = invoices_result.scalars().all()

    # Group by month and build records
    months_set: set[str] = set()
    records: dict[str, str] = {}

    for invoice in invoices:
        period = invoice.period  # Expected format: "2026-04"
        months_set.add(period)
        if invoice.student_group_id:
            key = f"{invoice.student_group_id}:{period}"
            # Map PaymentStatus to "paid" or "unpaid"
            status = "paid" if invoice.status == "paid" else "unpaid"
            records[key] = status

    months = sorted(list(months_set), reverse=True)

    return {
        "students": [
            {
                "id": s.id,
                "student_name": s.student_name,
            }
            for s in students
        ],
        "months": months,
        "records": records,
    }


# ─── Вкладка: Промежуточная успеваемость ─────────────────────────────────
@router.get("/group/{group_id}/grades")
async def get_group_grades(
    group_id: int,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Матрица успеваемости: студенты × занятия с оценками и комментариями."""
    group_meta_result = await db.execute(
        select(Group, Course, Teacher)
        .join(Course, Course.id == Group.course_id)
        .join(Lesson, Lesson.group_id == Group.id)
        .join(Teacher, Teacher.id == Lesson.teacher_id)
        .where(Group.id == group_id)
        .limit(1)
    )
    group_meta = group_meta_result.first()
    if not group_meta:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    group, course, teacher = group_meta

    group_result = await db.execute(
        select(StudentGroup)
        .where(
            and_(
                StudentGroup.group_id == group_id,
                StudentGroup.is_active == True,
            )
        )
        .order_by(StudentGroup.student_name)
    )
    students = group_result.scalars().all()

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    dt_from = datetime(effective_from.year, effective_from.month, effective_from.day, tzinfo=timezone.utc)
    dt_to = datetime(effective_to.year, effective_to.month, effective_to.day, 23, 59, 59, tzinfo=timezone.utc)

    _DOW_TO_WEEKDAY = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
    }

    # Get all lessons for this group
    lessons_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.status.in_([LessonStatus.scheduled, LessonStatus.completed, LessonStatus.rescheduled]),
            )
        )
    )
    lessons = lessons_result.scalars().all()

    # Generate lesson slots similar to matrix endpoint
    lesson_slots: list[dict] = []
    for lesson in lessons:
        if lesson.lesson_date is not None:
            ld = lesson.lesson_date
            ld_date = ld.date() if isinstance(ld, datetime) else ld
            if effective_from <= ld_date <= effective_to:
                lesson_slots.append({
                    "id": lesson.id,
                    "slot_date": ld_date.isoformat(),
                    "time_start": lesson.time_start.isoformat() if lesson.time_start else None,
                })
        elif lesson.day_of_week is not None:
            dow_raw = lesson.day_of_week
            dow_str = dow_raw.value if hasattr(dow_raw, 'value') else str(dow_raw)
            dow = _DOW_TO_WEEKDAY.get(dow_str.lower(), -1)
            if dow == -1:
                continue
            current = effective_from
            while current.weekday() != dow:
                current += timedelta(days=1)
            while current <= effective_to:
                lesson_slots.append({
                    "id": lesson.id,
                    "slot_date": current.isoformat(),
                    "time_start": lesson.time_start.isoformat() if lesson.time_start else None,
                })
                current += timedelta(days=7)

    lesson_slots.sort(key=lambda x: (x["slot_date"], x["time_start"] or ""))
    seen_slots: set[str] = set()
    unique_slots: list[dict] = []
    for slot in lesson_slots:
        k = f"{slot['id']}:{slot['slot_date']}"
        if k not in seen_slots:
            seen_slots.add(k)
            unique_slots.append(slot)

    student_ids = [s.id for s in students]
    attendance_records = []
    if student_ids:
        records_result = await db.execute(
            select(Attendance)
            .where(
                and_(
                    Attendance.student_group_id.in_(student_ids),
                    Attendance.lesson_date >= dt_from,
                    Attendance.lesson_date <= dt_to,
                )
            )
        )
        attendance_records = records_result.scalars().all()

    records: dict[str, dict] = {}
    attention_student_ids: set[int] = set()
    absent_counts: dict[int, int] = {}
    for record in attendance_records:
        lesson_date_key = record.lesson_date.date().isoformat() if isinstance(record.lesson_date, datetime) else str(record.lesson_date)
        key = f"{record.student_group_id}:{record.lesson_id}:{lesson_date_key}"
        records[key] = {
            "grade": record.grade,
            "note": record.note,
            "status": record.status.value if hasattr(record.status, 'value') else str(record.status),
        }
        if record.note:
            attention_student_ids.add(record.student_group_id)
        if record.status in (AttendanceStatus.absent, AttendanceStatus.late):
            absent_counts[record.student_group_id] = absent_counts.get(record.student_group_id, 0) + 1

    for student_id, count in absent_counts.items():
        if count >= 2:
            attention_student_ids.add(student_id)

    schedule_rows_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.status.in_([LessonStatus.scheduled, LessonStatus.completed, LessonStatus.rescheduled]),
            )
        )
        .order_by(Lesson.day_of_week, Lesson.time_start)
    )
    schedule_rows = schedule_rows_result.scalars().all()
    weekday_map = {
        'monday': 'Пн',
        'tuesday': 'Вт',
        'wednesday': 'Ср',
        'thursday': 'Чт',
        'friday': 'Пт',
        'saturday': 'Сб',
        'sunday': 'Вс',
    }
    schedule = []
    seen_schedule = set()
    for lesson in schedule_rows:
        dow_raw = lesson.day_of_week.value if hasattr(lesson.day_of_week, 'value') else str(lesson.day_of_week)
        label = f"{weekday_map.get(dow_raw, dow_raw[:2])} {lesson.time_start.strftime('%H:%M') if lesson.time_start else ''}".strip()
        if label not in seen_schedule:
            seen_schedule.add(label)
            schedule.append(label)

    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "course_name": course.name,
            "teacher_name": teacher.full_name,
            "schedule": schedule,
        },
        "students": [
            {
                "id": s.id,
                "student_name": s.student_name,
            }
            for s in students
        ],
        "lessons": unique_slots,
        "records": records,
        "attention_student_ids": sorted(attention_student_ids),
    }
