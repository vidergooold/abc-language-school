from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.branch import Branch
from app.models.group import Course, Group, StudentGroup, GroupStatus
from app.models.educational_program import EducationalProgram
from app.models.schedule import Lesson, Classroom
from app.models.teacher import Teacher
from app.schemas.schedule import LessonCreate
from app.schemas.group import (
    CourseCreate, CourseOut,
    GroupCreate, GroupOut,
    StudentGroupCreate, StudentGroupOut,
)
from app.schedule_rules import canonical_program_duration_minutes, derive_time_end, normalize_program_key
from app.api.v1.schedule import _normalize_lesson_payload, _validate_schedule_payload, check_schedule_conflicts


class GroupWithCourseOut(GroupOut):
    course: Optional[CourseOut] = None

    model_config = {"from_attributes": True}

router = APIRouter(tags=["Groups"])


def _build_group_name(language: str, program_name: str, *, is_individual: bool = False) -> str:
    language_key = normalize_program_key(language)
    program_key = normalize_program_key(program_name)
    if is_individual:
        prefix = "Инд."
        if program_key.startswith(language_key):
            return f"{prefix} {program_name}"
        return f"{prefix} {language} {program_name}".strip()
    if program_key.startswith(language_key):
        return program_name
    return f"{language} {program_name}".strip()


async def _resolve_course_for_program(
    db: AsyncSession,
    *,
    program_name: str,
    language: str,
) -> Optional[Course]:
    exact = await db.scalar(
        select(Course).where(
            Course.name == program_name,
            Course.is_active == True,
        )
    )
    if exact is not None:
        return exact

    same_language = await db.execute(
        select(Course).where(
            Course.language == language,
            Course.is_active == True,
        ).order_by(Course.name)
    )
    course = same_language.scalars().first()
    if course is not None:
        return course

    fallback = await db.execute(
        select(Course).where(Course.is_active == True).order_by(Course.name)
    )
    return fallback.scalars().first()


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
    language: Optional[str] = Query(None, description="Фильтр по языку группы (Английский / Китайский)"),
    active_only: bool = Query(True, description="Возвращать только активные/набирающиеся группы в учебных филиалах"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Group)
    if teacher_id is not None:
        query = query.where(Group.teacher_id == teacher_id)
    if language is not None:
        # Filter by course language using a subquery to avoid duplicate rows from joins
        course_ids_subq = select(Course.id).where(Course.language == language).scalar_subquery()
        query = query.where(Group.course_id.in_(course_ids_subq))
    if active_only:
        # Только активные или набирающиеся группы
        query = query.where(Group.status.in_([GroupStatus.active, GroupStatus.recruiting]))
        # Только группы, у которых есть хотя бы одно занятие в учебном (не административном) филиале
        teaching_lesson_exists = (
            select(Lesson.id)
            .join(Branch, Branch.id == Lesson.branch_id)
            .where(
                Lesson.group_id == Group.id,
                Branch.is_administrative.is_(False),
            )
            .correlate(Group)
            .exists()
        )
        query = query.where(teaching_lesson_exists)
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
    if data.program_id is not None:
        selected_language = (data.language or "").strip()
        program = await db.scalar(
            select(EducationalProgram).where(
                EducationalProgram.id == data.program_id,
                EducationalProgram.is_active == True,
            )
        )
        if program is None:
            raise HTTPException(status_code=404, detail="Программа не найдена")

        if normalize_program_key(program.language) != normalize_program_key(selected_language):
            raise HTTPException(status_code=400, detail="Программа не соответствует выбранному языку")

        teacher = await db.scalar(
            select(Teacher).where(Teacher.id == data.teacher_id, Teacher.is_active == True)
        )
        if teacher is None:
            raise HTTPException(status_code=404, detail="Преподаватель не найден")

        branch = await db.scalar(
            select(Branch).where(Branch.id == data.branch_id, Branch.is_active == True)
        )
        if branch is None:
            raise HTTPException(status_code=404, detail="Филиал не найден")

        classroom = await db.scalar(
            select(Classroom).where(Classroom.id == data.classroom_id, Classroom.is_active == True)
        )
        if classroom is None:
            raise HTTPException(status_code=404, detail="Кабинет не найден")
        if classroom.branch_id != branch.id:
            raise HTTPException(status_code=400, detail="Кабинет не относится к выбранному филиалу")

        course = await _resolve_course_for_program(
            db,
            program_name=program.name,
            language=program.language,
        )
        if course is None:
            raise HTTPException(status_code=404, detail="Подходящий курс не найден")

        group = Group(
            name=(data.name or _build_group_name(selected_language, program.name, is_individual=data.is_individual)).strip(),
            course_id=course.id,
            teacher_id=teacher.id,
            language=selected_language,
            program_name=program.name,
            is_individual=data.is_individual,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        db.add(group)
        await db.flush()

        lesson_duration = canonical_program_duration_minutes(program.name) or 90
        time_end = derive_time_end(data.time_start, lesson_duration)
        for lesson_day in data.lesson_days:
            lesson_data = LessonCreate(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                branch_id=branch.id,
                program_id=program.id,
                day_of_week=lesson_day,
                time_start=data.time_start,
                time_end=time_end,
                is_recurring=True,
            )
            lesson_data = await _normalize_lesson_payload(db, lesson_data)
            await _validate_schedule_payload(db, lesson_data)
            conflicts = await check_schedule_conflicts(
                db=db,
                group_id=lesson_data.group_id,
                teacher_id=lesson_data.teacher_id,
                classroom_id=lesson_data.classroom_id,
                day_of_week=lesson_day.value,
                time_start=lesson_data.time_start,
                time_end=lesson_data.time_end,
                lesson_date=lesson_data.lesson_date,
                is_recurring=lesson_data.is_recurring,
            )
            if conflicts:
                raise HTTPException(
                    status_code=409,
                    detail={"message": "Обнаружены конфликты расписания", "conflicts": conflicts},
                )
            db.add(
                Lesson(
                    group_id=lesson_data.group_id,
                    teacher_id=lesson_data.teacher_id,
                    classroom_id=lesson_data.classroom_id,
                    branch_id=lesson_data.branch_id,
                    program_id=lesson_data.program_id,
                    day_of_week=lesson_data.day_of_week,
                    time_start=lesson_data.time_start,
                    time_end=lesson_data.time_end,
                    topic=lesson_data.topic,
                    material_attachments=lesson_data.material_attachments,
                    is_recurring=lesson_data.is_recurring,
                    lesson_date=lesson_data.lesson_date,
                )
            )
    else:
        course = await db.scalar(select(Course).where(Course.id == data.course_id))
        if course is None:
            raise HTTPException(status_code=404, detail="Курс не найден")
        if data.teacher_id is not None:
            teacher = await db.scalar(
                select(Teacher).where(Teacher.id == data.teacher_id, Teacher.is_active == True)
            )
            if teacher is None:
                raise HTTPException(status_code=404, detail="Преподаватель не найден")
        group = Group(
            name=data.name,
            course_id=course.id,
            teacher_id=data.teacher_id,
            language=course.language,
            program_name=course.name,
            start_date=data.start_date,
            end_date=data.end_date,
        )
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
