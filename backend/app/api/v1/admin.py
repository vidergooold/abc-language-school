from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.models.forms import (
    ChildForm,
    AdultForm,
    PreschoolForm,
    TeacherForm,
    TestingForm,
    FeedbackForm,
)
from app.models.group import Group
from app.api.v1.users import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


def _fmt_dt(dt):
    """ISO-формат даты или None"""
    if dt is None:
        return None
    return dt.strftime("%d.%m.%Y %H:%M")


# ---------------------------------------------------------------------------
# GET /admin/forms
# ---------------------------------------------------------------------------
@router.get("/forms")
async def get_all_forms(
    limit: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить все формы заявок"""
    forms = []

    async with db as session:
        for model, type_label in [
            (ChildForm, "child"),
            (AdultForm, "adult"),
            (PreschoolForm, "preschool"),
            (TeacherForm, "teacher"),
            (TestingForm, "testing"),
        ]:
            result = await session.execute(select(model).order_by(model.id.desc()))
            for row in result.scalars().all():
                forms.append({
                    "id": row.id,
                    "type": type_label,
                    "fio": row.fio,
                    "phone": row.phone,
                    "email": getattr(row, "email", None),
                    "comment": getattr(row, "comment", None),
                    "status": getattr(row, "status", "new"),
                    "created_at": _fmt_dt(getattr(row, "created_at", None)),
                    "date": _fmt_dt(getattr(row, "created_at", None)),
                })

    forms.sort(key=lambda x: x["created_at"] or "", reverse=True)
    return forms[:limit] if limit else forms


# ---------------------------------------------------------------------------
# PATCH /admin/forms/{form_id}
# ---------------------------------------------------------------------------
@router.patch("/forms/{form_id}")
async def update_form(
    form_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Обновить статус или комментарий анкеты.

    Фронтенд передаёт { "status": "processed" }.
    Эндпоинт ищет запись во всех таблицах поочерёдно.
    """
    models = [ChildForm, AdultForm, PreschoolForm, TeacherForm, TestingForm]

    async with db as session:
        for model in models:
            row = await session.get(model, form_id)
            if row:
                for key, value in payload.items():
                    if hasattr(row, key):
                        setattr(row, key, value)
                await session.commit()
                return {"ok": True}

    raise HTTPException(status_code=404, detail="Form not found")


# ---------------------------------------------------------------------------
# DELETE /admin/forms/{form_id}
# ---------------------------------------------------------------------------
@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Удалить анкету по ID во всех типах."""
    models = [ChildForm, AdultForm, PreschoolForm, TeacherForm, TestingForm]

    async with db as session:
        for model in models:
            row = await session.get(model, form_id)
            if row:
                await session.delete(row)
                await session.commit()
                return {"ok": True}

    raise HTTPException(status_code=404, detail="Form not found")


# ---------------------------------------------------------------------------
# GET /admin/feedback
# ---------------------------------------------------------------------------
@router.get("/feedback")
async def get_all_feedback(
    limit: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить все сообщения обратной связи"""
    async with db as session:
        query = select(FeedbackForm).order_by(FeedbackForm.id.desc())
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        rows = result.scalars().all()

        return [
            {
                "id": fb.id,
                "name": fb.name,
                "phone": fb.phone,
                "email": fb.email,
                "message": fb.message,
                "is_read": fb.is_read,
                "created_at": _fmt_dt(fb.created_at),
                "date": _fmt_dt(fb.created_at),
            }
            for fb in rows
        ]


# ---------------------------------------------------------------------------
# PATCH /admin/feedback/{feedback_id}/read
# ---------------------------------------------------------------------------
@router.patch("/feedback/{feedback_id}/read")
async def mark_feedback_read(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Отметить сообщение как прочитанное."""
    async with db as session:
        fb = await session.get(FeedbackForm, feedback_id)
        if not fb:
            raise HTTPException(status_code=404, detail="Feedback not found")
        fb.is_read = True
        await session.commit()
        return {"ok": True}


# ---------------------------------------------------------------------------
# GET /admin/stats
# ---------------------------------------------------------------------------
@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Статистика для дашборда.

    Фронтенд ожидает поля:
      - total_forms      — всего анкет за всё время
      - total_students   — анкеты учеников (child + adult + preschool)
      - total_feedback   — всего обращений
      - schedule_groups  — групп в расписании (модель Group)
    """
    async with db as session:
        child_count = await session.scalar(select(func.count()).select_from(ChildForm))
        adult_count = await session.scalar(select(func.count()).select_from(AdultForm))
        preschool_count = await session.scalar(select(func.count()).select_from(PreschoolForm))
        teacher_count = await session.scalar(select(func.count()).select_from(TeacherForm))
        testing_count = await session.scalar(select(func.count()).select_from(TestingForm))
        feedback_count = await session.scalar(select(func.count()).select_from(FeedbackForm))
        groups_count = await session.scalar(select(func.count()).select_from(Group))

        total_forms = child_count + adult_count + preschool_count + teacher_count + testing_count
        total_students = child_count + adult_count + preschool_count

        return {
            # Ключи, которые ожидает Dashboard.vue
            "total_forms": total_forms,
            "total_students": total_students,
            "total_feedback": feedback_count,
            "schedule_groups": groups_count,
            # Дополнительная разбивка по типам
            "forms_by_type": {
                "child": child_count,
                "adult": adult_count,
                "preschool": preschool_count,
                "teacher": teacher_count,
                "testing": testing_count,
            },
        }


# ---------------------------------------------------------------------------
# GET /admin/students
# ---------------------------------------------------------------------------
@router.get("/students")
async def get_all_students(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить всех студентов (школьники + дошкольники + взрослые)"""
    students = []

    async with db as session:
        for model, type_label in [
            (ChildForm, "child"),
            (AdultForm, "adult"),
            (PreschoolForm, "preschool"),
        ]:
            result = await session.execute(select(model).order_by(model.id.desc()))
            for row in result.scalars().all():
                students.append({
                    "id": row.id,
                    "type": type_label,
                    "fio": row.fio,
                    "age": getattr(row, "age", None),
                    "phone": row.phone,
                    "email": getattr(row, "email", None),
                    "status": getattr(row, "status", "new"),
                    "created_at": _fmt_dt(getattr(row, "created_at", None)),
                })

    return students
