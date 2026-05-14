from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff, require_student
from app.models.group import StudentGroup, Group
from app.models.student import Student, StudentType, StudentStatus
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/students", tags=["Students"])


class StudentProfileOut(BaseModel):
    student: Optional[StudentOut] = None
    group: Optional[dict] = None


@router.get("", response_model=List[StudentOut])
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


@router.get("/me", response_model=StudentProfileOut)
async def get_my_student_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    student_result = await db.execute(select(Student).where(Student.email == current_user.email))
    student = student_result.scalar_one_or_none()

    group_result = await db.execute(
        select(StudentGroup, Group)
        .join(Group, Group.id == StudentGroup.group_id)
        .where(
            and_(
                StudentGroup.student_email == current_user.email,
                StudentGroup.is_active == True,
            )
        )
        .order_by(StudentGroup.enrolled_at.desc())
        .limit(1)
    )
    group_row = group_result.first()
    group_payload = None
    if group_row is not None:
        _, group = group_row
        group_payload = {
            "id": group.id,
            "name": group.name,
            "language": group.language,
            "program_name": group.program_name,
            "status": group.status.value if hasattr(group.status, "value") else str(group.status),
        }

    return {"student": student, "group": group_payload}


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
    _=Depends(require_admin),
):
    """Создать студента вручную — только администратор"""
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
    _=Depends(require_admin),
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


@router.patch("/{student_id}", response_model=StudentOut)
async def patch_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Частичное обновление студента — только администратор"""
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
