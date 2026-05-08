from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_admin
from app.models.teacher import Teacher, TeacherGroup
from app.models.schedule import Lesson, LessonStatus
from app.models.group import Group, Course
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut

router = APIRouter(prefix="/teachers", tags=["Teachers"])


class TeacherGroupAssign(BaseModel):
    group_id: int


class TeacherGroupOut(BaseModel):
    id: int
    teacher_id: int
    group_id: int
    group_name: Optional[str] = None
    course_name: Optional[str] = None

    model_config = {"from_attributes": True}


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


# ─── Группы преподавателя (many-to-many) ──────────────────────────────────────

@router.get("/{teacher_id}/groups", response_model=List[TeacherGroupOut])
async def get_teacher_groups(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Список групп, к которым назначен преподаватель"""
    teacher = await db.scalar(select(Teacher).where(Teacher.id == teacher_id))
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")

    result = await db.execute(
        select(TeacherGroup, Group.name.label("group_name"), Course.name.label("course_name"))
        .join(Group, TeacherGroup.group_id == Group.id)
        .join(Course, Group.course_id == Course.id)
        .where(TeacherGroup.teacher_id == teacher_id)
        .order_by(Group.name)
    )
    rows = result.all()
    return [
        TeacherGroupOut(
            id=row.TeacherGroup.id,
            teacher_id=row.TeacherGroup.teacher_id,
            group_id=row.TeacherGroup.group_id,
            group_name=row.group_name,
            course_name=row.course_name,
        )
        for row in rows
    ]


@router.post("/{teacher_id}/groups", response_model=TeacherGroupOut, status_code=201)
async def assign_teacher_to_group(
    teacher_id: int,
    data: TeacherGroupAssign,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Назначить преподавателя в группу"""
    teacher = await db.scalar(select(Teacher).where(Teacher.id == teacher_id))
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")

    group = await db.scalar(select(Group).where(Group.id == data.group_id))
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    existing = await db.scalar(
        select(TeacherGroup).where(
            TeacherGroup.teacher_id == teacher_id,
            TeacherGroup.group_id == data.group_id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Преподаватель уже назначен в эту группу")

    tg = TeacherGroup(teacher_id=teacher_id, group_id=data.group_id)
    db.add(tg)
    await db.commit()
    await db.refresh(tg)

    course = await db.scalar(select(Course).where(Course.id == group.course_id))
    return TeacherGroupOut(
        id=tg.id,
        teacher_id=tg.teacher_id,
        group_id=tg.group_id,
        group_name=group.name,
        course_name=course.name if course else None,
    )


@router.delete("/{teacher_id}/groups/{group_id}")
async def remove_teacher_from_group(
    teacher_id: int,
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Снять назначение преподавателя из группы"""
    tg = await db.scalar(
        select(TeacherGroup).where(
            TeacherGroup.teacher_id == teacher_id,
            TeacherGroup.group_id == group_id,
        )
    )
    if not tg:
        raise HTTPException(status_code=404, detail="Назначение не найдено")
    await db.delete(tg)
    await db.commit()
    return {"ok": True}
