from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.forms import (
    ChildForm,
    AdultForm,
    PreschoolForm,
    TeacherForm,
    TestingForm,
    FeedbackForm,
)
from app.api.v1.users import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/forms")
async def get_all_forms(
    limit: int = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить все формы заявок (школьники, взрослые, дошкольники, преподаватели, тестирование)"""
    forms = []
    
    # Получаем все типы форм
    async with db as session:
        # Школьники
        child_result = await session.execute(
            select(ChildForm).order_by(ChildForm.id.desc()).limit(limit) if limit else select(ChildForm).order_by(ChildForm.id.desc())
        )
        for form in child_result.scalars().all():
            forms.append({
                "id": form.id,
                "type": "child",
                "fio": form.fio,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Взрослые
        adult_result = await session.execute(
            select(AdultForm).order_by(AdultForm.id.desc()).limit(limit) if limit else select(AdultForm).order_by(AdultForm.id.desc())
        )
        for form in adult_result.scalars().all():
            forms.append({
                "id": form.id,
                "type": "adult",
                "fio": form.fio,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Дошкольники
        preschool_result = await session.execute(
            select(PreschoolForm).order_by(PreschoolForm.id.desc()).limit(limit) if limit else select(PreschoolForm).order_by(PreschoolForm.id.desc())
        )
        for form in preschool_result.scalars().all():
            forms.append({
                "id": form.id,
                "type": "preschool",
                "fio": form.fio,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Преподаватели
        teacher_result = await session.execute(
            select(TeacherForm).order_by(TeacherForm.id.desc()).limit(limit) if limit else select(TeacherForm).order_by(TeacherForm.id.desc())
        )
        for form in teacher_result.scalars().all():
            forms.append({
                "id": form.id,
                "type": "teacher",
                "fio": form.fio,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Тестирование
        testing_result = await session.execute(
            select(TestingForm).order_by(TestingForm.id.desc()).limit(limit) if limit else select(TestingForm).order_by(TestingForm.id.desc())
        )
        for form in testing_result.scalars().all():
            forms.append({
                "id": form.id,
                "type": "testing",
                "fio": form.fio,
                "phone": form.phone,
                "email": None,
                "created_at": form.created_at,
            })
    
    # Сортируем по дате создания
    forms.sort(key=lambda x: x["created_at"], reverse=True)
    
    return forms[:limit] if limit else forms


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
        feedback_list = result.scalars().all()
        
        return [
            {
                "id": fb.id,
                "name": fb.name,
                "phone": fb.phone,
                "email": fb.email,
                "message": fb.message,
                "created_at": fb.created_at,
            }
            for fb in feedback_list
        ]


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить статистику по заявкам"""
    async with db as session:
        # Подсчет всех типов форм
        child_count = await session.scalar(select(func.count()).select_from(ChildForm))
        adult_count = await session.scalar(select(func.count()).select_from(AdultForm))
        preschool_count = await session.scalar(select(func.count()).select_from(PreschoolForm))
        teacher_count = await session.scalar(select(func.count()).select_from(TeacherForm))
        testing_count = await session.scalar(select(func.count()).select_from(TestingForm))
        feedback_count = await session.scalar(select(func.count()).select_from(FeedbackForm))
        
        return {
            "totalForms": child_count + adult_count + preschool_count + teacher_count + testing_count,
            "totalFeedback": feedback_count,
            "formsByType": {
                "child": child_count,
                "adult": adult_count,
                "preschool": preschool_count,
                "teacher": teacher_count,
                "testing": testing_count,
            },
        }


@router.get("/students")
async def get_all_students(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_admin),
):
    """Получить всех студентов (школьники + дошкольники + взрослые)"""
    students = []
    
    async with db as session:
        # Школьники
        child_result = await session.execute(select(ChildForm).order_by(ChildForm.id.desc()))
        for form in child_result.scalars().all():
            students.append({
                "id": form.id,
                "type": "child",
                "fio": form.fio,
                "age": form.age,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Взрослые
        adult_result = await session.execute(select(AdultForm).order_by(AdultForm.id.desc()))
        for form in adult_result.scalars().all():
            students.append({
                "id": form.id,
                "type": "adult",
                "fio": form.fio,
                "age": form.age,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
        
        # Дошкольники
        preschool_result = await session.execute(select(PreschoolForm).order_by(PreschoolForm.id.desc()))
        for form in preschool_result.scalars().all():
            students.append({
                "id": form.id,
                "type": "preschool",
                "fio": form.fio,
                "age": form.age,
                "phone": form.phone,
                "email": form.email,
                "created_at": form.created_at,
            })
    
    return students
