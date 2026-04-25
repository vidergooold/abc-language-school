from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.teacher import Teacher
from app.models.schedule import Lesson, LessonStatus
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/", response_model=List[TeacherOut])
async def get_teachers(
    branch_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Публичный список активных преподавателей"""
    base_query = select(Teacher).where(Teacher.is_active == True)

    # Если выбран филиал, сначала пробуем отфильтровать по расписанию в этом филиале.
    if branch_id is not None:
        filtered_query = (
            base_query
            .join(Lesson, Lesson.teacher_id == Teacher.id)
            .where(
                Lesson.branch_id == branch_id,
                Lesson.status.in_([LessonStatus.scheduled, LessonStatus.rescheduled]),
            )
            .distinct()
            .order_by(Teacher.full_name)
        )
        filtered_result = await db.execute(filtered_query)
        filtered_teachers = filtered_result.scalars().all()
        if filtered_teachers:
            return filtered_teachers

    result = await db.execute(base_query.order_by(Teacher.full_name))
    return result.scalars().all()


@router.get("/all", response_model=List[TeacherOut])
async def get_all_teachers(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Все преподаватели (включая неактивных) — только для администратора"""
    result = await db.execute(select(Teacher).order_by(Teacher.full_name))
    return result.scalars().all()


@router.get("/{teacher_id}", response_model=TeacherOut)
async def get_teacher(teacher_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    return teacher


@router.post("/", response_model=TeacherOut)
async def create_teacher(
    data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Создать преподавателя — только администратор"""
    existing = await db.execute(select(Teacher).where(Teacher.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Преподаватель с таким email уже существует")
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.put("/{teacher_id}", response_model=TeacherOut)
async def update_teacher(
    teacher_id: int,
    data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}")
async def deactivate_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Деактивировать преподавателя (мягкое удаление)"""
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    teacher.is_active = False
    await db.commit()
    return {"ok": True, "message": "Преподаватель деактивирован"}
