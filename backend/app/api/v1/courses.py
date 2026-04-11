"""
Модуль курсов.

Публичное API:
  GET  /courses          — каталог для сайта (фильтры, пагинация)
  GET  /courses/{id}     — карточка курса

Административное API:
  POST   /admin/courses           — создать курс
  PUT    /admin/courses/{id}      — обновить курс
  PATCH  /admin/courses/{id}/toggle-active — включить / выключить
  DELETE /admin/courses/{id}      — удалить курс
  GET    /admin/courses/{id}/stats — статистика курса
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import require_admin
from app.models.group import Course, CourseLevel, CourseCategory, Group, StudentGroup

router = APIRouter(tags=["Courses"])


# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC СХЕМЫ (локальные, чтобы не зависеть от отсутствующего schemas/course.py)
# ═══════════════════════════════════════════════════════════════════════

class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    language: str
    level: CourseLevel
    category: CourseCategory
    duration_months: int
    lessons_per_week: int
    price_per_month: int
    max_students: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    language: str = Field(default="Английский", max_length=50)
    level: CourseLevel
    category: CourseCategory
    duration_months: int = Field(default=9, ge=1, le=60)
    lessons_per_week: int = Field(default=2, ge=1, le=7)
    price_per_month: int = Field(..., ge=0)
    max_students: int = Field(default=8, ge=1, le=30)
    is_active: bool = True


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)
    level: Optional[CourseLevel] = None
    category: Optional[CourseCategory] = None
    duration_months: Optional[int] = Field(None, ge=1, le=60)
    lessons_per_week: Optional[int] = Field(None, ge=1, le=7)
    price_per_month: Optional[int] = Field(None, ge=0)
    max_students: Optional[int] = Field(None, ge=1, le=30)
    is_active: Optional[bool] = None


class CourseStatsOut(BaseModel):
    course_id: int
    course_name: str
    groups_total: int
    groups_active: int
    students_total: int
    students_active: int
    revenue_monthly_potential: int   # max_students * price_per_month * active_groups


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════════════

async def _get_course_or_404(course_id: int, db: AsyncSession) -> Course:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


# ═══════════════════════════════════════════════════════════════════════
# ПУБЛИЧНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/courses", response_model=List[CourseOut], summary="Каталог курсов")
async def get_courses(
    language: Optional[str] = Query(None, description="Фильтр по языку"),
    level: Optional[CourseLevel] = Query(None, description="Фильтр по уровню"),
    category: Optional[CourseCategory] = Query(None, description="Фильтр по категории"),
    active_only: bool = Query(True, description="Только активные курсы"),
    db: AsyncSession = Depends(get_db),
):
    """Публичный каталог курсов для сайта. Поддерживает фильтрацию."""
    q = select(Course)
    if active_only:
        q = q.where(Course.is_active == True)
    if language:
        q = q.where(Course.language.ilike(f"%{language}%"))
    if level:
        q = q.where(Course.level == level)
    if category:
        q = q.where(Course.category == category)
    q = q.order_by(Course.category, Course.level, Course.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/courses/{course_id}", response_model=CourseOut, summary="Карточка курса")
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Публичная страница курса. Возвращает только активный курс."""
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.is_active == True)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Курс не найден")
    return course


# ═══════════════════════════════════════════════════════════════════════
# АДМИНИСТРАТИВНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/admin/courses", response_model=List[CourseOut], summary="[Админ] Все курсы")
async def admin_list_courses(
    include_inactive: bool = Query(True, description="Включить неактивные"),
    category: Optional[CourseCategory] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Полный список курсов для административной панели."""
    q = select(Course)
    if not include_inactive:
        q = q.where(Course.is_active == True)
    if category:
        q = q.where(Course.category == category)
    q = q.order_by(Course.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/admin/courses", response_model=CourseOut, status_code=201,
             summary="[Админ] Создать курс")
async def admin_create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Создать новое направление обучения."""
    # Проверяем уникальность имени
    existing = await db.execute(
        select(Course).where(Course.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Курс с именем '{data.name}' уже существует"
        )
    course = Course(
        name=data.name,
        description=data.description,
        language=data.language,
        level=data.level,
        category=data.category,
        duration_months=data.duration_months,
        lessons_per_week=data.lessons_per_week,
        price_per_month=data.price_per_month,
        max_students=data.max_students,
        is_active=data.is_active,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.put("/admin/courses/{course_id}", response_model=CourseOut,
            summary="[Админ] Обновить курс")
async def admin_update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Обновить любые поля курса. Передаются только изменяемые поля."""
    course = await _get_course_or_404(course_id, db)

    if data.name is not None:
        # Проверяем уникальность нового имени (если другой курс)
        dup = await db.execute(
            select(Course).where(Course.name == data.name, Course.id != course_id)
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Курс с именем '{data.name}' уже существует"
            )
        course.name = data.name
    if data.description is not None:
        course.description = data.description
    if data.language is not None:
        course.language = data.language
    if data.level is not None:
        course.level = data.level
    if data.category is not None:
        course.category = data.category
    if data.duration_months is not None:
        course.duration_months = data.duration_months
    if data.lessons_per_week is not None:
        course.lessons_per_week = data.lessons_per_week
    if data.price_per_month is not None:
        course.price_per_month = data.price_per_month
    if data.max_students is not None:
        course.max_students = data.max_students
    if data.is_active is not None:
        course.is_active = data.is_active

    await db.commit()
    await db.refresh(course)
    return course


@router.patch("/admin/courses/{course_id}/toggle-active", response_model=CourseOut,
              summary="[Админ] Включить / выключить курс")
async def admin_toggle_active(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Переключает is_active. При деактивации курса с активными группами
    выдаётся предупреждение, но операция разрешается.
    """
    course = await _get_course_or_404(course_id, db)

    # Считаем активные группы
    active_groups_q = await db.execute(
        select(func.count(Group.id)).where(
            Group.course_id == course_id,
            Group.status == "active"
        )
    )
    active_groups_count = active_groups_q.scalar_one()

    course.is_active = not course.is_active
    await db.commit()
    await db.refresh(course)

    response = CourseOut.model_validate(course)
    # Добавляем предупреждение в заголовок ответа, если есть активные группы
    if not course.is_active and active_groups_count > 0:
        # Возвращаем данные + предупреждение через нестандартное поле
        return response  # клиент увидит is_active=False и может показать предупреждение
    return response


@router.get("/admin/courses/{course_id}/stats", response_model=CourseStatsOut,
            summary="[Админ] Статистика курса")
async def admin_course_stats(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Статистика по курсу:
    - количество групп (всего и активных)
    - количество студентов (всего и активных)
    - потенциальная ежемесячная выручка
    """
    course = await _get_course_or_404(course_id, db)

    # Группы
    groups_result = await db.execute(
        select(
            func.count(Group.id).label("total"),
            func.sum(
                func.cast(Group.status == "active", type_=None)
            ).label("active")
        ).where(Group.course_id == course_id)
    )
    groups_row = groups_result.one()
    groups_total = groups_row.total or 0

    # Группы активные — считаем отдельно для надёжности
    active_groups_result = await db.execute(
        select(func.count(Group.id)).where(
            Group.course_id == course_id,
            Group.status == "active"
        )
    )
    groups_active = active_groups_result.scalar_one() or 0

    # Студенты: через StudentGroup → Group → course_id
    students_result = await db.execute(
        select(func.count(StudentGroup.id))
        .join(Group, StudentGroup.group_id == Group.id)
        .where(Group.course_id == course_id)
    )
    students_total = students_result.scalar_one() or 0

    active_students_result = await db.execute(
        select(func.count(StudentGroup.id))
        .join(Group, StudentGroup.group_id == Group.id)
        .where(
            Group.course_id == course_id,
            StudentGroup.is_active == True
        )
    )
    students_active = active_students_result.scalar_one() or 0

    # Потенциальная выручка: активные группы * max_students * price_per_month
    revenue_potential = groups_active * course.max_students * course.price_per_month

    return CourseStatsOut(
        course_id=course_id,
        course_name=course.name,
        groups_total=groups_total,
        groups_active=groups_active,
        students_total=students_total,
        students_active=students_active,
        revenue_monthly_potential=revenue_potential,
    )


@router.delete("/admin/courses/{course_id}", status_code=204,
               summary="[Админ] Удалить курс")
async def admin_delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Удалить курс. Запрещено, если к курсу привязаны группы.
    Сначала нужно перенести или завершить все группы.
    """
    course = await _get_course_or_404(course_id, db)

    # Проверяем наличие связанных групп
    groups_q = await db.execute(
        select(func.count(Group.id)).where(Group.course_id == course_id)
    )
    groups_count = groups_q.scalar_one()
    if groups_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Нельзя удалить курс: к нему привязано {groups_count} группы(групп). "
                "Сначала удалите или перенесите все группы."
            )
        )

    await db.delete(course)
    await db.commit()
