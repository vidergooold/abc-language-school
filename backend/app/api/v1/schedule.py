"""Schedule router.

Матрица доступа:
  GET  /classrooms          — require_staff  (учитель видит аудитории)
  POST /classrooms          — require_admin
  GET  /schedule            — require_staff  (учитель видит расписание)
  POST /schedule            — require_admin
  PUT  /schedule/{id}       — require_admin
  DELETE /schedule/{id}     — require_admin
  POST /schedule/check      — require_staff  (проверка конфликтов без сохранения)
"""
from typing import List
from datetime import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.schedule import Lesson, Classroom, LessonStatus
from app.schemas.schedule import LessonCreate, LessonOut, ClassroomCreate, ClassroomOut

router = APIRouter(tags=["Schedule"])


# ─── Вспомогательная функция: проверка конфликтов ─────────────────────────────
async def check_schedule_conflicts(
    db: AsyncSession,
    group_id: int,
    teacher_id: int,
    classroom_id: int,
    day_of_week: str,
    time_start: time,
    time_end: time,
    exclude_lesson_id: int = None,
) -> list[dict]:
    """
    Проверяет три типа конфликтов в расписании:
      1. Группа: нельзя назначить группу на два занятия одновременно
      2. Преподаватель: нельзя поставить преподавателя в два места одновременно
      3. Аудитория: нельзя занять один кабинет двумя группами одновременно

    Два занятия конфликтуют по времени если:
      new.time_start < existing.time_end AND new.time_end > existing.time_start
    """
    conflicts = []
    active_statuses = [LessonStatus.scheduled, LessonStatus.rescheduled]

    def time_overlaps(s1: time, e1: time, s2: time, e2: time) -> bool:
        return s1 < e2 and e1 > s2

    base_filter = and_(
        Lesson.day_of_week == day_of_week,
        Lesson.status.in_(active_statuses),
    )
    if exclude_lesson_id:
        base_filter = and_(base_filter, Lesson.id != exclude_lesson_id)

    # 1. Конфликт группы
    group_result = await db.execute(
        select(Lesson).where(and_(base_filter, Lesson.group_id == group_id))
    )
    for lesson in group_result.scalars().all():
        if time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "group",
                "message": f"Группа уже имеет занятие в {lesson.time_start}–{lesson.time_end} ({day_of_week})",
                "conflicting_lesson_id": lesson.id,
            })

    # 2. Конфликт преподавателя
    teacher_result = await db.execute(
        select(Lesson).where(and_(base_filter, Lesson.teacher_id == teacher_id))
    )
    for lesson in teacher_result.scalars().all():
        if time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "teacher",
                "message": f"Преподаватель уже занят в {lesson.time_start}–{lesson.time_end} ({day_of_week})",
                "conflicting_lesson_id": lesson.id,
            })

    # 3. Конфликт аудитории
    classroom_result = await db.execute(
        select(Lesson).where(and_(base_filter, Lesson.classroom_id == classroom_id))
    )
    for lesson in classroom_result.scalars().all():
        if time_overlaps(time_start, time_end, lesson.time_start, lesson.time_end):
            conflicts.append({
                "conflict_type": "classroom",
                "message": f"Аудитория занята в {lesson.time_start}–{lesson.time_end} ({day_of_week})",
                "conflicting_lesson_id": lesson.id,
            })

    return conflicts


# ─── Аудитории ────────────────────────────────────────────────────────────────────
@router.get("/classrooms", response_model=List[ClassroomOut])
async def get_classrooms(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),  # Учитель должен видеть аудитории
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


# ─── Занятия ────────────────────────────────────────────────────────────────────
@router.get("/schedule", response_model=List[LessonOut])
async def get_schedule(
    group_id: int = None,
    teacher_id: int = None,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_staff),  # Учитель должен видеть расписание
):
    """Получить расписание. Можно фильтровать по группе или преподавателю."""
    query = select(Lesson).where(
        Lesson.status.in_([LessonStatus.scheduled, LessonStatus.rescheduled])
    )
    if group_id:
        query = query.where(Lesson.group_id == group_id)
    if teacher_id:
        query = query.where(Lesson.teacher_id == teacher_id)
    result = await db.execute(query.order_by(Lesson.day_of_week, Lesson.time_start))
    return result.scalars().all()


@router.post("/schedule", response_model=LessonOut)
async def create_lesson(
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    """
    Создать занятие в расписании.
    ПЕРЕД сохранением выполняется проверка трёх видов конфликтов:
    - группа уже занята в это время
    - преподаватель уже занят в это время
    - аудитория уже занята в это время
    Если найден хотя бы один конфликт — возвращается 409 с подробным описанием.
    """
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=data.day_of_week,
        time_start=data.time_start,
        time_end=data.time_end,
    )
    if conflicts:
        raise HTTPException(
            status_code=409,
            detail={"message": "Обнаружены конфликты расписания", "conflicts": conflicts},
        )
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


@router.put("/schedule/{lesson_id}", response_model=LessonOut)
async def update_lesson(
    lesson_id: int,
    data: LessonCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Обновить занятие с повторной проверкой конфликтов (исключая само занятие)"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=data.day_of_week,
        time_start=data.time_start,
        time_end=data.time_end,
        exclude_lesson_id=lesson_id,
    )
    if conflicts:
        raise HTTPException(
            status_code=409,
            detail={"message": "Обнаружены конфликты расписания", "conflicts": conflicts},
        )
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
    _: None = Depends(require_staff),  # Учитель может проверять конфликты
):
    """Предварительная проверка конфликтов без сохранения занятия"""
    conflicts = await check_schedule_conflicts(
        db=db,
        group_id=data.group_id,
        teacher_id=data.teacher_id,
        classroom_id=data.classroom_id,
        day_of_week=data.day_of_week,
        time_start=data.time_start,
        time_end=data.time_end,
    )
    return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts}
