from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.attendance import get_group_grades
from app.core.database import get_db
from app.core.security import require_staff, require_student
from app.models.attendance import Attendance
from app.models.group import StudentGroup
from app.models.schedule import DayOfWeek, Lesson, LessonStatus
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress"])


class ProgressDateCreate(BaseModel):
    group_id: int
    lesson_date: date


class ProgressDateUpdate(BaseModel):
    new_date: date


_PYTHON_WEEKDAY_TO_DAY_OF_WEEK = {
    0: DayOfWeek.monday,
    1: DayOfWeek.tuesday,
    2: DayOfWeek.wednesday,
    3: DayOfWeek.thursday,
    4: DayOfWeek.friday,
    5: DayOfWeek.saturday,
    6: DayOfWeek.sunday,
}

_ACTIVE_LESSON_STATUSES = [
    LessonStatus.scheduled,
    LessonStatus.rescheduled,
    LessonStatus.completed,
]


def _weekday_to_day_of_week(weekday: int) -> DayOfWeek:
    day_of_week = _PYTHON_WEEKDAY_TO_DAY_OF_WEEK.get(weekday)
    if day_of_week is None:
        raise HTTPException(status_code=400, detail="Некорректная дата занятия")
    return day_of_week


@router.get("")
@router.get("/")
async def get_progress(
    group_id: int = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    return await get_group_grades(
        group_id=group_id,
        date_from=date_from,
        date_to=date_to,
        db=db,
    )


@router.get("/my")
async def get_my_progress(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    student_group_result = await db.execute(
        select(StudentGroup)
        .where(
            and_(
                StudentGroup.student_email == current_user.email,
                StudentGroup.is_active == True,
            )
        )
        .order_by(StudentGroup.enrolled_at.desc())
        .limit(1)
    )
    student_group = student_group_result.scalar_one_or_none()
    if student_group is None:
        return {
            "group": None,
            "students": [],
            "lessons": [],
            "records": {},
            "attention_student_ids": [],
            "averages": {},
        }

    payload = await get_group_grades(
        group_id=student_group.group_id,
        date_from=date_from,
        date_to=date_to,
        db=db,
    )

    student_id = student_group.id
    student_key = str(student_id)
    student_payload = next((s for s in payload.get("students", []) if s.get("id") == student_id), None)
    filtered_records = {
        key: value
        for key, value in (payload.get("records", {}) or {}).items()
        if key.startswith(f"{student_id}:")
    }

    return {
        "group": payload.get("group"),
        "student": student_payload,
        "lessons": payload.get("lessons", []),
        "records": filtered_records,
        "averages": payload.get("averages", {}).get(student_key, {"month": None, "academic_year": None}),
    }


@router.post("/dates")
async def create_progress_date(
    payload: ProgressDateCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    template_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == payload.group_id,
                Lesson.status.in_(_ACTIVE_LESSON_STATUSES),
                Lesson.time_start.is_not(None),
                Lesson.time_end.is_not(None),
            )
        )
        .order_by(Lesson.is_recurring.desc(), Lesson.time_start.asc(), Lesson.id.asc())
    )
    template = template_result.scalars().first()
    if template is None:
        raise HTTPException(status_code=400, detail="Для группы нет шаблона занятия")

    duplicate_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.group_id == payload.group_id,
                func.date(Lesson.lesson_date) == payload.lesson_date,
                Lesson.time_start == template.time_start,
                Lesson.time_end == template.time_end,
                Lesson.status.in_(_ACTIVE_LESSON_STATUSES),
            )
        )
    )
    if duplicate_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="Эта дата уже добавлена")

    weekday_enum = _weekday_to_day_of_week(payload.lesson_date.weekday())
    new_lesson = Lesson(
        group_id=payload.group_id,
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


@router.patch("/dates/{lesson_id}")
async def update_progress_date(
    lesson_id: int,
    payload: ProgressDateUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    lesson_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.id == lesson_id,
                Lesson.is_recurring.is_(False),
                Lesson.lesson_date.is_not(None),
            )
        )
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Дата занятия для редактирования не найдена")

    old_date = lesson.lesson_date.date() if isinstance(lesson.lesson_date, datetime) else lesson.lesson_date
    if payload.new_date == old_date:
        return {"id": lesson.id, "slot_date": payload.new_date.isoformat()}

    duplicate_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.group_id == lesson.group_id,
                Lesson.id != lesson.id,
                func.date(Lesson.lesson_date) == payload.new_date,
                Lesson.time_start == lesson.time_start,
                Lesson.time_end == lesson.time_end,
                Lesson.status.in_(_ACTIVE_LESSON_STATUSES),
            )
        )
    )
    if duplicate_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail="На эту дату уже есть занятие с тем же временем")

    lesson.lesson_date = datetime.combine(payload.new_date, datetime.min.time())
    lesson.day_of_week = _weekday_to_day_of_week(payload.new_date.weekday())

    attendance_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == lesson.id,
                func.date(Attendance.lesson_date) == old_date,
            )
        )
    )
    for row in attendance_result.scalars().all():
        row.lesson_date = datetime.combine(payload.new_date, datetime.min.time())

    await db.commit()
    return {"id": lesson.id, "slot_date": payload.new_date.isoformat()}


@router.delete("/dates/{lesson_id}")
async def delete_progress_date(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    lesson_result = await db.execute(
        select(Lesson).where(
            and_(
                Lesson.id == lesson_id,
                Lesson.is_recurring.is_(False),
                Lesson.lesson_date.is_not(None),
            )
        )
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Дата занятия для удаления не найдена")

    slot_date = lesson.lesson_date.date() if isinstance(lesson.lesson_date, datetime) else lesson.lesson_date
    attendance_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.lesson_id == lesson.id,
                func.date(Attendance.lesson_date) == slot_date,
            )
        )
    )
    for row in attendance_result.scalars().all():
        await db.delete(row)

    await db.delete(lesson)
    await db.commit()
    return {"ok": True}
