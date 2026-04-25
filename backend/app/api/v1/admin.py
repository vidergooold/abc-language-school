from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import require_admin
from app.models.forms import (
    ChildForm,
    AdultForm,
    PreschoolForm,
    TeacherForm,
    TestingForm,
    FeedbackForm,
    TaxForm,
)
from app.models.group import Group
from app.models.student import Student
from app.models.teacher import Teacher

router = APIRouter(prefix="/admin", tags=["Admin"])


def _fmt_dt(dt):
    """ISO-формат даты или None"""
    if dt is None:
        return None
    return dt.strftime("%d.%m.%Y %H:%M")


def _serialize_form_details(row):
    """Сериализация всех полей анкеты (кроме служебных) для админ-интерфейса."""
    excluded = {"id", "status", "comment", "created_at"}
    details = {}

    for col in row.__table__.columns:
        key = col.name
        if key in excluded:
            continue
        value = getattr(row, key, None)
        if isinstance(value, (datetime, date)):
            value = _fmt_dt(value)
        details[key] = value

    return details


# ---------------------------------------------------------------------------
# GET /admin/forms
# ---------------------------------------------------------------------------
@router.get("/forms")
async def get_all_forms(
    limit: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Получить все формы заявок"""
    forms = []

    for model, type_label in [
        (ChildForm, "child"),
        (AdultForm, "adult"),
        (PreschoolForm, "preschool"),
        (TeacherForm, "teacher"),
        (TestingForm, "testing"),
        (TaxForm, "tax"),
    ]:
        result = await db.execute(select(model).order_by(model.id.desc()))
        for row in result.scalars().all():
            forms.append({
                "id": row.id,
                "type": type_label,
                "fio": getattr(row, "fio", None) or getattr(row, "payer_fio", None) or "—",
                "phone": getattr(row, "phone", None) or getattr(row, "payer_phone", None),
                "email": getattr(row, "email", None),
                "comment": getattr(row, "comment", None),
                "status": getattr(row, "status", "new"),
                "created_at": _fmt_dt(getattr(row, "created_at", None)),
                "date": _fmt_dt(getattr(row, "created_at", None)),
                "details": _serialize_form_details(row),
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
    _=Depends(require_admin),
):
    """Обновить статус или комментарий анкеты."""
    models = [ChildForm, AdultForm, PreschoolForm, TeacherForm, TestingForm, TaxForm]

    for model in models:
        row = await db.get(model, form_id)
        if row:
            for key, value in payload.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            await db.commit()
            return {"ok": True}

    raise HTTPException(status_code=404, detail="Form not found")


# ---------------------------------------------------------------------------
# DELETE /admin/forms/{form_id}
# ---------------------------------------------------------------------------
@router.delete("/forms/{form_id}")
async def delete_form(
    form_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Удалить анкету по ID во всех типах."""
    models = [ChildForm, AdultForm, PreschoolForm, TeacherForm, TestingForm, TaxForm]

    for model in models:
        row = await db.get(model, form_id)
        if row:
            await db.delete(row)
            await db.commit()
            return {"ok": True}

    raise HTTPException(status_code=404, detail="Form not found")


# ---------------------------------------------------------------------------
# GET /admin/feedback
# ---------------------------------------------------------------------------
@router.get("/feedback")
async def get_all_feedback(
    limit: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Получить все сообщения обратной связи"""
    query = select(FeedbackForm).order_by(FeedbackForm.id.desc())
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
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
    _=Depends(require_admin),
):
    """Отметить сообщение как прочитанное."""
    fb = await db.get(FeedbackForm, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    fb.is_read = True
    await db.commit()
    return {"ok": True}


# ---------------------------------------------------------------------------
# GET /admin/stats
# ---------------------------------------------------------------------------
@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Статистика для дашборда.

    Фронтенд ожидает:
      total_forms, total_students, total_feedback, schedule_groups
    """
    child_count     = await db.scalar(select(func.count()).select_from(ChildForm))
    adult_count     = await db.scalar(select(func.count()).select_from(AdultForm))
    preschool_count = await db.scalar(select(func.count()).select_from(PreschoolForm))
    teacher_count   = await db.scalar(select(func.count()).select_from(TeacherForm))
    testing_count   = await db.scalar(select(func.count()).select_from(TestingForm))
    tax_count       = await db.scalar(select(func.count()).select_from(TaxForm))
    feedback_count  = await db.scalar(select(func.count()).select_from(FeedbackForm))
    groups_count    = await db.scalar(select(func.count()).select_from(Group))
    student_count   = await db.scalar(select(func.count()).select_from(Student))
    teacher_db_count = await db.scalar(select(func.count()).select_from(Teacher))

    total_forms    = child_count + adult_count + preschool_count + teacher_count + testing_count + tax_count
    total_students = student_count

    return {
        "total_forms":     total_forms,
        "total_students":  total_students,
        "total_teachers":  teacher_db_count,
        "total_feedback":  feedback_count,
        "schedule_groups": groups_count,
        "forms_by_type": {
            "child":     child_count,
            "adult":     adult_count,
            "preschool": preschool_count,
            "teacher":   teacher_count,
            "testing":   testing_count,
            "tax":       tax_count,
        },
    }


# ---------------------------------------------------------------------------
# GET /admin/students
# ---------------------------------------------------------------------------
@router.get("/students")
async def get_all_students(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Получить всех студентов (школьники + дошкольники + взрослые)"""
    students = []

    for model, type_label in [
        (ChildForm, "child"),
        (AdultForm, "adult"),
        (PreschoolForm, "preschool"),
    ]:
        result = await db.execute(select(model).order_by(model.id.desc()))
        for row in result.scalars().all():
            students.append({
                "id":         row.id,
                "type":       type_label,
                "fio":        row.fio,
                "age":        getattr(row, "age", None),
                "phone":      row.phone,
                "email":      getattr(row, "email", None),
                "status":     getattr(row, "status", "new"),
                "created_at": _fmt_dt(getattr(row, "created_at", None)),
            })

    return students
