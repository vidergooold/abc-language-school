from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.homework import Homework
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.schemas.homework import HomeworkCreate, HomeworkUpdate, HomeworkOut

router = APIRouter(prefix="/homeworks", tags=["Homeworks"])


async def _resolve_teacher_id(db: AsyncSession, current_user: User) -> Optional[int]:
    result = await db.execute(
        select(Teacher.id).where(Teacher.email == current_user.email, Teacher.is_active == True)
    )
    return result.scalar_one_or_none()


@router.get("/", response_model=List[HomeworkOut])
async def get_homeworks(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
    group_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
):
    """Получить домашние задания с фильтрацией"""
    q = select(Homework)
    if group_id:
        q = q.where(Homework.group_id == group_id)
    if teacher_id:
        q = q.where(Homework.teacher_id == teacher_id)
    q = q.order_by(Homework.due_date.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{homework_id}", response_model=HomeworkOut)
async def get_homework(
    homework_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    result = await db.execute(select(Homework).where(Homework.id == homework_id))
    homework = result.scalar_one_or_none()
    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    return homework


@router.post("/", response_model=HomeworkOut)
async def create_homework(
    data: HomeworkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """Создать домашнее задание — администратор или преподаватель (только своё)"""
    if current_user.role == UserRole.teacher:
        teacher_id = await _resolve_teacher_id(db, current_user)
        if teacher_id is None:
            raise HTTPException(status_code=403, detail="Профиль преподавателя не найден")
        if data.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Можно создавать задания только для себя")
    homework = Homework(**data.model_dump())
    db.add(homework)
    await db.commit()
    await db.refresh(homework)
    return homework


@router.put("/{homework_id}", response_model=HomeworkOut)
async def update_homework(
    homework_id: int,
    data: HomeworkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    result = await db.execute(select(Homework).where(Homework.id == homework_id))
    homework = result.scalar_one_or_none()
    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    if current_user.role == UserRole.teacher:
        teacher_id = await _resolve_teacher_id(db, current_user)
        if teacher_id is None or homework.teacher_id != teacher_id:
            raise HTTPException(status_code=403, detail="Можно редактировать только свои задания")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(homework, field, value)
    await db.commit()
    await db.refresh(homework)
    return homework


@router.delete("/{homework_id}")
async def delete_homework(
    homework_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Удалить домашнее задание — только администратор"""
    result = await db.execute(select(Homework).where(Homework.id == homework_id))
    homework = result.scalar_one_or_none()
    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")
    await db.delete(homework)
    await db.commit()
    return {"ok": True, "message": "Домашнее задание удалено"}
