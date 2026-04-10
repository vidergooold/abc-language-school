from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.attendance import Attendance, AttendanceStatus
from app.models.group import StudentGroup
from app.schemas.attendance import AttendanceCreate, AttendanceOut, AttendanceStats

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceOut)
async def mark_attendance(
    data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Отметить посещаемость для студента на занятии"""
    # Проверяем, не отмечали ли уже
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
    _=Depends(require_admin),
):
    """Список присутствия на конкретном занятии"""
    result = await db.execute(
        select(Attendance).where(Attendance.lesson_id == lesson_id)
    )
    return result.scalars().all()


@router.get("/student/{student_group_id}/stats", response_model=AttendanceStats)
async def get_student_attendance_stats(
    student_group_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Статистика посещаемости одного студента"""
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

    total = len(records)
    present = sum(1 for r in records if r.status == AttendanceStatus.present)
    absent = sum(1 for r in records if r.status == AttendanceStatus.absent)
    late = sum(1 for r in records if r.status == AttendanceStatus.late)
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
    _=Depends(require_admin),
):
    """Сводка посещаемости всей группы"""
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
        total = len(records)
        present = sum(1 for r in records if r.status == AttendanceStatus.present)
        summary.append({
            "student_id": student.id,
            "student_name": student.student_name,
            "total": total,
            "present": present,
            "rate": round(present / total * 100, 1) if total > 0 else 0.0,
        })

    return summary
