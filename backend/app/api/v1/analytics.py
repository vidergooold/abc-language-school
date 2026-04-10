from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.payment import Invoice, Payment, PaymentStatus
from app.models.group import Group, Course, StudentGroup
from app.models.schedule import Lesson, LessonStatus
from app.models.attendance import Attendance
from app.models.waitlist import WaitlistEntry, WaitlistStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/unit-economics")
async def get_unit_economics(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Unit-экономика на одного ученика:
    - Средний чек (ARPU)
    - Средняя длительность обучения в месяцах (LT)
    - LTV = ARPU × LT
    - Доля оплат от начислений (collection rate)
    Считается по всей базе: Invoice + StudentGroup.
    """
    # Средний чек: средняя сумма счёта
    avg_invoice = await db.scalar(
        select(func.avg(Invoice.amount)).where(Invoice.status != PaymentStatus.refunded)
    ) or Decimal(0)

    # Всего уникальных студентов
    total_students = await db.scalar(
        select(func.count()).select_from(StudentGroup)
    ) or 1

    # Всего начислено и оплачено
    total_invoiced = await db.scalar(select(func.sum(Invoice.amount))) or Decimal(0)
    total_paid     = await db.scalar(select(func.sum(Invoice.amount_paid))) or Decimal(0)

    collection_rate = round(float(total_paid / total_invoiced * 100), 1) if total_invoiced > 0 else 0

    # Среднее кол-во счетов на студента ≈ длительность обучения в месяцах
    total_invoices_count = await db.scalar(select(func.count()).select_from(Invoice)) or 0
    avg_lt = round(total_invoices_count / total_students, 1)

    arpu = float(avg_invoice)
    ltv  = round(arpu * avg_lt, 2)

    return {
        "arpu":            arpu,
        "avg_lt_months":   avg_lt,
        "ltv":             ltv,
        "collection_rate": collection_rate,
        "total_students":  total_students,
        "total_invoiced":  float(total_invoiced),
        "total_paid":      float(total_paid),
    }


@router.get("/revenue-scenarios")
async def get_revenue_scenarios(
    price_per_month: int = Query(4500, description="Цена обучения в месяц (руб.)"),
    fixed_costs:     int = Query(80000, description="Постоянные расходы в месяц (руб.)"),
    variable_cost_per_student: int = Query(500, description="Переменные расходы на ученика (руб.)"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Три сценария выручки и прибыли:
    - Пессимистичный: 30 учеников
    - Базовый:        60 учеников
    - Оптимистичный:  100 учеников

    Для каждого считаем:
      revenue  = students × price_per_month
      costs    = fixed_costs + students × variable_cost
      profit   = revenue - costs
      margin   = profit / revenue × 100 %
      payback  = fixed_costs / profit (мес., если profit > 0)
    """
    scenarios = [
        {"name": "Пессимистичный", "students": 30},
        {"name": "Базовый",        "students": 60},
        {"name": "Оптимистичный",  "students": 100},
    ]
    result = []
    for s in scenarios:
        n       = s["students"]
        revenue = n * price_per_month
        costs   = fixed_costs + n * variable_cost_per_student
        profit  = revenue - costs
        margin  = round(profit / revenue * 100, 1) if revenue > 0 else 0
        payback = round(fixed_costs / profit, 1) if profit > 0 else None
        result.append({
            "scenario":         s["name"],
            "students":         n,
            "revenue":          revenue,
            "fixed_costs":      fixed_costs,
            "variable_costs":   n * variable_cost_per_student,
            "total_costs":      costs,
            "profit":           profit,
            "margin_pct":       margin,
            "payback_months":   payback,
        })
    return result


@router.get("/break-even")
async def get_break_even(
    price_per_month: int = Query(4500),
    fixed_costs:     int = Query(80000),
    variable_cost_per_student: int = Query(500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Точка безубыточности:
    BEP (учеников) = fixed_costs / (price - variable_cost_per_student)
    BEP (выручка)  = BEP_students × price
    Margin of safety = (actual_students - BEP_students) / actual_students × 100%
    """
    contribution_margin = price_per_month - variable_cost_per_student
    if contribution_margin <= 0:
        return {"error": "Маржинальная прибыль ≤ 0, BEP не достигается"}

    bep_students = round(fixed_costs / contribution_margin, 1)
    bep_revenue  = round(bep_students * price_per_month, 2)

    # Фактическое число активных студентов
    actual_students = await db.scalar(
        select(func.count()).select_from(StudentGroup).where(StudentGroup.is_active == True)
    ) or 0

    safety_margin_pct = (
        round((actual_students - bep_students) / actual_students * 100, 1)
        if actual_students > 0 else None
    )

    return {
        "contribution_margin":     contribution_margin,
        "bep_students":            bep_students,
        "bep_revenue":             bep_revenue,
        "actual_students":         actual_students,
        "safety_margin_pct":       safety_margin_pct,
        "is_profitable":           actual_students >= bep_students,
    }


@router.get("/sensitivity")
async def get_sensitivity_analysis(
    price_per_month: int = Query(4500),
    fixed_costs:     int = Query(80000),
    variable_cost_per_student: int = Query(500),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Анализ чувствительности: как меняется прибыль при разном числе учеников.
    Шаг: каждые 10 учеников от 10 до 120.
    """
    rows = []
    for n in range(10, 130, 10):
        revenue = n * price_per_month
        costs   = fixed_costs + n * variable_cost_per_student
        profit  = revenue - costs
        rows.append({
            "students": n,
            "revenue":  revenue,
            "costs":    costs,
            "profit":   profit,
            "is_profitable": profit > 0,
        })
    return rows


@router.get("/teacher-load")
async def get_teacher_load(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Загрузка преподавателей:
    - Количество активных занятий в неделю
    - Количество групп
    - Количество студентов
    """
    from app.models.teacher import Teacher
    teachers_result = await db.execute(select(Teacher).where(Teacher.is_active == True))
    teachers = teachers_result.scalars().all()

    report = []
    for teacher in teachers:
        lessons_count = await db.scalar(
            select(func.count()).select_from(Lesson)
            .where(and_(Lesson.teacher_id == teacher.id,
                        Lesson.status == LessonStatus.scheduled))
        ) or 0
        groups_count = await db.scalar(
            select(func.count(Lesson.group_id.distinct())).select_from(Lesson)
            .where(and_(Lesson.teacher_id == teacher.id,
                        Lesson.status == LessonStatus.scheduled))
        ) or 0
        report.append({
            "teacher_id":     teacher.id,
            "teacher_name":   teacher.full_name,
            "lessons_per_week": lessons_count,
            "groups_count":   groups_count,
        })
    return report


@router.get("/course-popularity")
async def get_course_popularity(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Популярность курсов:
    - Количество активных студентов
    - Количество групп
    - Количество человек в листе ожидания
    - Доля заполненности групп
    """
    courses_result = await db.execute(select(Course).where(Course.is_active == True))
    courses = courses_result.scalars().all()

    report = []
    for course in courses:
        students_count = await db.scalar(
            select(func.count()).select_from(StudentGroup)
            .join(Group, Group.id == StudentGroup.group_id)
            .where(and_(Group.course_id == course.id, StudentGroup.is_active == True))
        ) or 0
        groups_count = await db.scalar(
            select(func.count()).select_from(Group).where(Group.course_id == course.id)
        ) or 0
        waitlist_count = await db.scalar(
            select(func.count()).select_from(WaitlistEntry)
            .where(and_(WaitlistEntry.course_id == course.id,
                        WaitlistEntry.status == WaitlistStatus.waiting))
        ) or 0
        max_capacity = groups_count * course.max_students if groups_count > 0 else course.max_students
        fill_rate = round(students_count / max_capacity * 100, 1) if max_capacity > 0 else 0

        report.append({
            "course_id":      course.id,
            "course_name":    course.name,
            "language":       course.language,
            "level":          course.level,
            "students_count": students_count,
            "groups_count":   groups_count,
            "waitlist_count": waitlist_count,
            "fill_rate_pct":  fill_rate,
            "price_per_month": course.price_per_month,
        })
    return sorted(report, key=lambda x: x["students_count"], reverse=True)


@router.get("/enrollment-funnel")
async def get_enrollment_funnel(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Воронка записи:
    1. Заявки (forms) → 2. Лист ожидания → 3. Зачислены → 4. Активны сейчас
    Показывает конверсию на каждом шаге.
    """
    from app.models.forms import AdultForm
    total_forms = await db.scalar(select(func.count()).select_from(AdultForm)) or 0
    waitlisted  = await db.scalar(
        select(func.count()).select_from(WaitlistEntry)
    ) or 0
    enrolled_ever = await db.scalar(
        select(func.count()).select_from(StudentGroup)
    ) or 0
    active_now = await db.scalar(
        select(func.count()).select_from(StudentGroup).where(StudentGroup.is_active == True)
    ) or 0

    def conv(a, b):
        return round(a / b * 100, 1) if b > 0 else 0

    return [
        {"stage": "Заявки",            "count": total_forms,   "conversion_pct": 100},
        {"stage": "Лист ожидания",     "count": waitlisted,    "conversion_pct": conv(waitlisted, total_forms)},
        {"stage": "Когда-либо зачислен","count": enrolled_ever, "conversion_pct": conv(enrolled_ever, total_forms)},
        {"stage": "Активны сейчас",    "count": active_now,    "conversion_pct": conv(active_now, total_forms)},
    ]
