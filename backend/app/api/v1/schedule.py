"""Schedule router.

Матрица доступа:
    GET  /schedule/my         — require_student (пользователь видит своё расписание)
    GET  /schedule             — require_staff  (учитель видит всё расписание)
    POST /schedule             — require_staff  (учитель только для своих занятий)
    PUT  /schedule/{id}        — require_staff  (учитель только для своих занятий)
    DELETE /schedule/{id}      — require_admin
  POST /schedule/check       — require_staff
  GET  /classrooms           — require_staff
  POST /classrooms           — require_admin
"""
from typing import List, Optional
from datetime import datetime, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff, require_student
from app.models.schedule import Lesson, Classroom, LessonStatus
from app.models.room_booking import RoomBooking, BookingStatus
from app.models.group import StudentGroup, Group, Course
from app.models.teacher import Teacher
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.schemas.schedule import (
    LessonCardOut,
    LessonCreate,
    LessonListOut,
    LessonManageOut,
    ClassroomCreate,
    ClassroomOut,
)
from app.models.user import User, UserRole

router = APIRouter(tags=["Schedule"])


DAY_OF_WEEK_BY_INDEX = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def _enum_value(value):
    return value.value if hasattr(value, "value") else value


async def _resolve_teacher_id_for_user(db: AsyncSession, current_user: User) -> Optional[int]:
    result = await db.execute(
        select(Teacher.id).where(
            Teacher.email == current_user.email,
            Teacher.is_active == True,
        )
    )
    return result.scalar_one_or_none()


def _time_overlaps(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and end_a > start_b


def _lesson_day_key(lesson_date: Optional[datetime], fallback_day: str) -> str:
    if lesson_date is None:
        return fallback_day
    return DAY_OF_WEEK_BY_INDEX[lesson_date.weekday()]


def _booking_matches_lesson(
    booking: RoomBooking,
    day_of_week: str,
    lesson_date: Optional[datetime],
    is_recurring: bool,
) -> bool:
    if lesson_date is not None:
        return booking.booking_date == lesson_date.date()

    if not booking.is_recurring:
        return DAY_OF_WEEK_BY_INDEX[booking.booking_date.weekday()] == day_of_week

    recurrence_rule = (booking.recurrence_rule or "").upper()
    if recurrence_rule:
        short_day = {
            "monday": "MON",
            "tuesday": "TUE",
            "wednesday": "WED",
            "thursday": "THU",
            "friday": "FRI",
            "saturday": "SAT",
            "sunday": "SUN",
        }[day_of_week]
        return short_day in recurrence_rule

    return DAY_OF_WEEK_BY_INDEX[booking.booking_date.weekday()] == day_of_week


def _lessons_share_calendar_slot(
    existing_lesson: Lesson,
    day_of_week: str,
    lesson_date: Optional[datetime],
) -> bool:
    if lesson_date is not None:
        if existing_lesson.lesson_date is not None:
            return existing_lesson.lesson_date.date() == lesson_date.date()
        return _enum_value(existing_lesson.day_of_week) == DAY_OF_WEEK_BY_INDEX[lesson_date.weekday()]

    if existing_lesson.lesson_date is not None:
        return DAY_OF_WEEK_BY_INDEX[existing_lesson.lesson_date.weekday()] == day_of_week

    return _enum_value(existing_lesson.day_of_week) == day_of_week


async def _validate_schedule_payload(db: AsyncSession, data: LessonCreate) -> None:
    if data.time_start >= data.time_end:
        raise HTTPException(status_code=400, detail="Время окончания должно быть позже времени начала")

    if data.lesson_date is not None:
        expected_day = DAY_OF_WEEK_BY_INDEX[data.lesson_date.weekday()]
        if _enum_value(data.day_of_week) != expected_day:
            raise HTTPException(
                status_code=400,
                detail="Дата занятия не соответствует выбранному дню недели",
            )

    group = await db.scalar(select(Group).where(Group.id == data.group_id))
    if group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    teacher = await db.scalar(
        select(Teacher).where(Teacher.id == data.teacher_id, Teacher.is_active == True)
    )
    if teacher is None:
        raise HTTPException(status_code=404, detail="Преподаватель не найден или неактивен")

    classroom = await db.scalar(
        select(Classroom).where(Classroom.id == data.classroom_id, Classroom.is_active == True)
    )
    if classroom is None:
        raise HTTPException(status_code=404, detail="Аудитория не найдена или неактивна")

    if data.branch_id is not None:
        branch = await db.scalar(
            select(Branch).where(Branch.id == data.branch_id, Branch.is_active == True)
        )
        if branch is None:
            raise HTTPException(status_code=404, detail="Филиал не найден или неактивен")

    if data.program_id is not None:
        program = await db.scalar(
            select(EducationalProgram).where(
                EducationalProgram.id == data.program_id,
                EducationalProgram.is_active == True,
            )
        )
        if program is None:
            raise HTTPException(status_code=404, detail="Образовательная программа не найдена или неактивна")

    if group.start_date and data.lesson_date and data.lesson_date < group.start_date:
        raise HTTPException(status_code=400, detail="Дата занятия раньше даты старта группы")

    if group.end_date and data.lesson_date and data.lesson_date > group.end_date:
        raise HTTPException(status_code=400, detail="Дата занятия позже даты завершения группы")


def _build_schedule_query():
    return (
        select(
            Lesson.id,
            Lesson.group_id,
            Lesson.teacher_id,
            Lesson.classroom_id,
            Lesson.branch_id,
            Lesson.program_id,
            Lesson.day_of_week,
            Lesson.time_start,
            Lesson.time_end,
            Lesson.topic,
            Lesson.status,
            Lesson.is_recurring,
            Lesson.lesson_date,
            Lesson.created_at,
            Group.name.label("group_name"),
            Course.name.label("course_name"),
            Course.level.label("course_level"),
            Teacher.full_name.label("teacher_name"),
            Classroom.name.label("classroom_name"),
            Branch.name.label("branch_name"),
            EducationalProgram.name.label("program_name"),
        )
        .select_from(Lesson)
        .join(Group, Lesson.group_id == Group.id)
        .join(Course, Group.course_id == Course.id)
        .join(Teacher, Lesson.teacher_id == Teacher.id)
        .join(Classroom, Lesson.classroom_id == Classroom.id)
        .outerjoin(Branch, Lesson.branch_id == Branch.id)
        .outerjoin(EducationalProgram, Lesson.program_id == EducationalProgram.id)
    )


def _serialize_schedule_row(row) -> dict:
    return {
        "id": row.id,
        "group_id": row.group_id,
        "teacher_id": row.teacher_id,
        "classroom_id": row.classroom_id,
        "branch_id": row.branch_id,
        "program_id": row.program_id,
        "day_of_week": _enum_value(row.day_of_week),
        "time_start": row.time_start,
        "time_end": row.time_end,
        "topic": row.topic,
        "status": _enum_value(row.status),
        "is_recurring": row.is_recurring,
        "lesson_date": row.lesson_date,
        "created_at": row.created_at,
        "group_name": row.group_name,
        "course_name": row.course_name,
        "teacher_name": row.teacher_name,
        "classroom_name": row.classroom_name,
        "branch_name": row.branch_name,
        "program_name": row.program_name,
        "level": _enum_value(row.course_level),
    }


# ─── Вспомогательная функция: проверка конфликтов ───────────────────────────────
async def check_schedule_conflicts(
    db: AsyncSession,
    group_id: int,
    teacher_id: int,
    classroom_id: int,
    day_of_week: str,
    time_start: time,
    time_end: time,
    lesson_date: Optional[datetime] = None,
    is_recurring: bool = True,
    exclude_lesson_id: int = None,
) -> list[dict]:
    conflicts = []
    active_statuses = [LessonStatus.scheduled, LessonStatus.rescheduled]

    base_filter = Lesson.status.in_(active_statuses)
    if exclude_lesson_id:
        base_filter = and_(base_filter, Lesson.id != exclude_lesson_id)

    group_lessons = (
        await db.execute(select(Lesson).where(and_(base_filter, Lesson.group_id == group_id)))
    ).scalars().all()
    for lesson in group_lessons:
        if not _lessons_share_calendar_slot(lesson, day_of_week, lesson_date):
            continue
        if _time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "group",
                "message": f"Группа уже имеет занятие в {lesson.time_start.strftime('%H:%M')}–{lesson.time_end.strftime('%H:%M')}",
                "conflicting_lesson_id": lesson.id,
            })

    # Получаем имя преподавателя для информативного сообщения
    teacher = await db.scalar(select(Teacher).where(Teacher.id == teacher_id))
    teacher_full_name = teacher.full_name if teacher else f"ID {teacher_id}"

    day_labels = {
        "monday": "понедельник", "tuesday": "вторник", "wednesday": "среду",
        "thursday": "четверг", "friday": "пятницу", "saturday": "субботу", "sunday": "воскресенье",
    }
    day_label = day_labels.get(day_of_week, day_of_week)

    teacher_lessons = (
        await db.execute(select(Lesson).where(and_(base_filter, Lesson.teacher_id == teacher_id)))
    ).scalars().all()
    for lesson in teacher_lessons:
        if not _lessons_share_calendar_slot(lesson, day_of_week, lesson_date):
            continue
        if _time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "teacher",
                "message": (
                    f"Преподаватель {teacher_full_name} уже занят в {day_label} "
                    f"с {lesson.time_start.strftime('%H:%M')} до {lesson.time_end.strftime('%H:%M')}"
                ),
                "teacher_full_name": teacher_full_name,
                "conflicting_lesson_id": lesson.id,
            })

    classroom_lessons = (
        await db.execute(select(Lesson).where(and_(base_filter, Lesson.classroom_id == classroom_id)))
    ).scalars().all()
    for lesson in classroom_lessons:
        if not _lessons_share_calendar_slot(lesson, day_of_week, lesson_date):
            continue
        if _time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "classroom",
                "message": f"Аудитория занята уроком в {lesson.time_start.strftime('%H:%M')}–{lesson.time_end.strftime('%H:%M')}",
                "conflicting_lesson_id": lesson.id,
            })

    booking_filter = and_(
        RoomBooking.classroom_id == classroom_id,
        RoomBooking.status == BookingStatus.confirmed,
    )
    if lesson_date is not None:
        booking_filter = and_(booking_filter, RoomBooking.booking_date == lesson_date.date())
    room_bookings = (await db.execute(select(RoomBooking).where(booking_filter))).scalars().all()
    for booking in room_bookings:
        if not _booking_matches_lesson(booking, day_of_week, lesson_date, is_recurring):
            continue
        if _time_overlaps(time_start, time_end, booking.time_start, booking.time_end):
            conflicts.append({
                "conflict_type": "classroom_booking",
                "message": f"Аудитория уже забронирована в {booking.time_start.strftime('%H:%M')}–{booking.time_end.strftime('%H:%M')}",
                "conflicting_lesson_id": booking.id,
            })

    return conflicts


# ─── Расписание пользователя ───────────────────────────────────────────────────────────────
@router.get("/schedule/my", response_model=List[LessonCardOut])
async def get_my_schedule(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    """Расписание текущего пользователя: студент видит свои группы, учитель свои уроки, админ всё."""
    day_map = {
        "monday": "Пн",
        "tuesday": "Вт",
        "wednesday": "Ср",
        "thursday": "Чт",
        "friday": "Пт",
        "saturday": "Сб",
        "sunday": "Вс",
    }

    query = _build_schedule_query().where(
        Lesson.status.in_([LessonStatus.scheduled, LessonStatus.rescheduled])
    )

    if current_user.role == 'student':
        sg_result = await db.execute(
            select(StudentGroup.group_id).where(
                and_(
                    StudentGroup.student_email == current_user.email,
                    StudentGroup.is_active == True,
                )
            )
        )
        group_ids = [row[0] for row in sg_result.all()]
        if not group_ids:
            return []
        query = query.where(Lesson.group_id.in_(group_ids))
    elif current_user.role == 'teacher':
        teacher_result = await db.execute(
            select(Teacher.id).where(
                Teacher.email == current_user.email,
                Teacher.is_active == True,
            )
        )
        teacher_id = teacher_result.scalar_one_or_none()
        if teacher_id is None:
            return []
        query = query.where(Lesson.teacher_id == teacher_id)

    result = await db.execute(query.order_by(Lesson.day_of_week, Lesson.time_start))
    rows = result.all()

    schedule = []
    for row in rows:
        day_key = _enum_value(row.day_of_week)
        day = day_map.get(day_key, day_key)
        time_str = f"{row.time_start.strftime('%H:%M')}–{row.time_end.strftime('%H:%M')}"
        schedule.append({
            "id": row.id,
            "day": day,
            "course": row.course_name,
            "time": time_str,
            "teacher": row.teacher_name,
            "place": row.classroom_name,
            "level": _enum_value(row.course_level),
            "lesson_date": row.lesson_date,
        })

    return schedule


# ─── Аудитории ───────────────────────────────────────────────────────────────────────────
@router.get("/classrooms", response_model=List[ClassroomOut])
async def get_classrooms(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    result = await db.execute(
        select(Classroom).where(Classroom.is_active == True).order_by(Classroom.name)
    )
    return result.scalars().all()


@router.post("/classrooms", response_model=ClassroomOut)
async def create_classroom(
    data: ClassroomCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    classroom = Classroom(**data.model_dump())
    db.add(classroom)
    await db.commit()
    await db.refresh(classroom)
    return classroom


# ─── Занятия ──────────────────────────────────────────────────────────────────────────────
@router.get("/schedule", response_model=List[LessonListOut])
async def get_schedule(
    group_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    query = _build_schedule_query().where(
        Lesson.status.in_([LessonStatus.scheduled, LessonStatus.rescheduled])
    )

    if group_id:
        query = query.where(Lesson.group_id == group_id)
    if teacher_id:
        query = query.where(Lesson.teacher_id == teacher_id)

    result = await db.execute(query.order_by(Lesson.day_of_week, Lesson.time_start))
    rows = result.all()
    return [_serialize_schedule_row(row) for row in rows]


@router.post("/schedule", response_model=LessonManageOut)
async def create_lesson(
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    if current_user.role == UserRole.teacher:
        teacher_id = await _resolve_teacher_id_for_user(db, current_user)
        if teacher_id is None:
            raise HTTPException(status_code=403, detail="Профиль преподавателя не найден")
        if data.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Можно создавать только свои занятия")

    await _validate_schedule_payload(db, data)
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=_lesson_day_key(data.lesson_date, _enum_value(data.day_of_week)),
        time_start=data.time_start,
        time_end=data.time_end,
        lesson_date=data.lesson_date,
        is_recurring=data.is_recurring,
    )
    if conflicts:
        teacher_conflicts = [c for c in conflicts if c["conflict_type"] == "teacher"]
        if teacher_conflicts:
            raise HTTPException(status_code=409, detail=teacher_conflicts[0]["message"])
        raise HTTPException(
            status_code=409,
            detail={"message": "Обнаружены конфликты расписания", "conflicts": conflicts},
        )
    group = await db.scalar(select(Group).where(Group.id == data.group_id))
    if group is not None:
        group.teacher_id = data.teacher_id
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.put("/schedule/{lesson_id}", response_model=LessonManageOut)
async def update_lesson(
    lesson_id: int,
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    if current_user.role == UserRole.teacher:
        teacher_id = await _resolve_teacher_id_for_user(db, current_user)
        if teacher_id is None:
            raise HTTPException(status_code=403, detail="Профиль преподавателя не найден")
        if lesson.teacher_id != teacher_id or data.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Можно редактировать только свои занятия")

    await _validate_schedule_payload(db, data)
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=_lesson_day_key(data.lesson_date, _enum_value(data.day_of_week)),
        time_start=data.time_start,
        time_end=data.time_end,
        lesson_date=data.lesson_date,
        is_recurring=data.is_recurring,
        exclude_lesson_id=lesson_id,
    )
    if conflicts:
        teacher_conflicts = [c for c in conflicts if c["conflict_type"] == "teacher"]
        if teacher_conflicts:
            raise HTTPException(status_code=409, detail=teacher_conflicts[0]["message"])
        raise HTTPException(
            status_code=409,
            detail={"message": "Обнаружены конфликты расписания", "conflicts": conflicts},
        )
    group = await db.scalar(select(Group).where(Group.id == data.group_id))
    if group is not None:
        group.teacher_id = data.teacher_id
    for field, value in data.model_dump().items():
        setattr(lesson, field, value)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.delete("/schedule/{lesson_id}")
async def cancel_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    lesson.status = LessonStatus.cancelled
    await db.commit()
    return {"ok": True}


@router.post("/schedule/check-conflicts")
async def check_conflicts_only(
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),
):
    await _validate_schedule_payload(db, data)
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=_lesson_day_key(data.lesson_date, _enum_value(data.day_of_week)),
        time_start=data.time_start,
        time_end=data.time_end,
        lesson_date=data.lesson_date,
        is_recurring=data.is_recurring,
    )
    return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts}
