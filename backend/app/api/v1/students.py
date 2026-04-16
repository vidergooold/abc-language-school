from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.student import Student, StudentType, StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=List[StudentOut])
async def get_students(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
    student_type: Optional[StudentType] = Query(None),
    status: Optional[StudentStatus] = Query(None),
    search: Optional[str] = Query(None),
):
    """Список студентов с фильтрацией — для сотрудников"""
    q = select(Student)
    if student_type:
        q = q.where(Student.student_type == student_type)
    if status:
        q = q.where(Student.status == status)
    if search:
        q = q.where(
            or_(
                Student.full_name.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%"),
            )
        )
    q = q.order_by(Student.full_name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student


@router.post("/", response_model=StudentOut)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Создать студента вручную — для сотрудников"""
    student = Student(**data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}")
async def deactivate_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Деактивировать студента — только администратор"""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    student.is_active = False
    await db.commit()
    return {"ok": True, "message": "Студент деактивирован"}
