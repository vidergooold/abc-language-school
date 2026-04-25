from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.group import Course, Group, StudentGroup, GroupStatus
from app.models.schedule import Lesson
from app.models.teacher import Teacher
from app.schemas.group import (
    CourseCreate, CourseOut,
    GroupCreate, GroupOut,
    StudentGroupCreate, StudentGroupOut,
)


class GroupWithCourseOut(GroupOut):
    course: Optional[CourseOut] = None

    model_config = {"from_attributes": True}

router = APIRouter(tags=["Groups"])


# ─── Курсы ───────────────────────────────────────────────────────────

@router.get("/courses", response_model=List[CourseOut])
async def get_courses(db: AsyncSession = Depends(get_db)):
    """Публичный список активных курсов"""
    result = await db.execute(
        select(Course).where(Course.is_active == True).order_by(Course.name)
    )
    return result.scalars().all()


@router.post("/courses", response_model=CourseOut)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.put("/courses/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: int,
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    for field, value in data.model_dump().items():
        setattr(course, field, value)
    await db.commit()
    await db.refresh(course)
    return course


# ─── Группы ──────────────────────────────────────────────────────────

@router.get("/groups", response_model=List[GroupOut])
async def get_groups(
    branch_id: Optional[int] = Query(None),
    teacher_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    query = select(Group)
    if teacher_id is not None:
        query = query.where(Group.teacher_id == teacher_id)
    if branch_id is not None:
        query = query.join(Lesson, Lesson.group_id == Group.id)
        query = query.where(Lesson.branch_id == branch_id)
        query = query.distinct()
    result = await db.execute(query.order_by(Group.created_at.desc()))
    return result.scalars().all()


@router.get("/groups/{group_id}", response_model=GroupWithCourseOut)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Group).options(selectinload(Group.course)).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group


@router.post("/groups", response_model=GroupOut)
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    course = await db.execute(select(Course).where(Course.id == data.course_id))
    if not course.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Курс не найден")
    if data.teacher_id is not None:
        teacher = await db.execute(select(Teacher).where(Teacher.id == data.teacher_id, Teacher.is_active == True))
        if not teacher.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Преподаватель не найден")
    group = Group(**data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.put("/groups/{group_id}/status")
async def update_group_status(
    group_id: int,
    status: GroupStatus,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    group.status = status
    await db.commit()
    return {"ok": True, "status": status}


# ─── Студенты в группах ───────────────────────────────────────────────

@router.get("/groups/{group_id}/students", response_model=List[StudentGroupOut])
async def get_group_students(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),  # учитель тоже может видеть студентов
):
    result = await db.execute(
        select(StudentGroup)
        .where(StudentGroup.group_id == group_id, StudentGroup.is_active == True)
        .order_by(StudentGroup.student_name)
    )
    return result.scalars().all()


@router.post("/groups/{group_id}/students", response_model=StudentGroupOut)
async def add_student_to_group(
    group_id: int,
    data: StudentGroupCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    group_result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = group_result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    course_result = await db.execute(
        select(Course).where(Course.id == group.course_id)
    )
    course = course_result.scalar_one_or_none()

    count_result = await db.execute(
        select(func.count()).select_from(StudentGroup)
        .where(StudentGroup.group_id == group_id, StudentGroup.is_active == True)
    )
    current_count = count_result.scalar()

    if course and current_count >= course.max_students:
        raise HTTPException(
            status_code=400,
            detail=f"Группа заполнена. Максимум: {course.max_students} студентов"
        )

    student = StudentGroup(group_id=group_id, **{k: v for k, v in data.model_dump().items() if k != 'group_id'})
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/groups/{group_id}/students/{student_id}")
async def remove_student_from_group(
    group_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(
        select(StudentGroup)
        .where(StudentGroup.id == student_id, StudentGroup.group_id == group_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден в этой группе")
    student.is_active = False
    await db.commit()
    return {"ok": True}
