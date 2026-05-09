"""Materials endpoint — alias for GET /attendance/group/{group_id}/materials.

Exposes GET /materials?group_id={id} so the frontend page LessonMaterial.vue
can fetch lesson materials without knowing the internal attendance route path.
"""
from datetime import date, datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_staff
from app.models.group import Group
from app.models.schedule import Lesson, LessonStatus

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get("")
@router.get("/")
async def list_materials(
    group_id: int = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """
    Список материалов (тем) уроков для группы в указанном периоде.

    Принимает group_id как query-параметр (не path-параметр), чтобы
    фронтенд мог делать GET /api/v1/materials?group_id={id}.
    """
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    if not group_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Группа не найдена")

    effective_from = date_from or (date.today() - timedelta(days=60))
    effective_to = date_to or date.today()

    dt_from = datetime(effective_from.year, effective_from.month, effective_from.day, tzinfo=timezone.utc)
    dt_to = datetime(effective_to.year, effective_to.month, effective_to.day, 23, 59, 59, tzinfo=timezone.utc)

    materials_result = await db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.group_id == group_id,
                Lesson.topic.isnot(None),
                Lesson.status.in_([LessonStatus.scheduled, LessonStatus.completed, LessonStatus.rescheduled]),
            )
        )
        .order_by(Lesson.lesson_date.desc() if Lesson.lesson_date else Lesson.day_of_week)
    )
    lessons = materials_result.scalars().all()

    materials = []
    for lesson in lessons:
        if lesson.lesson_date:
            ld = lesson.lesson_date.date() if isinstance(lesson.lesson_date, datetime) else lesson.lesson_date
            if dt_from.date() <= ld <= dt_to.date():
                materials.append({
                    "id": lesson.id,
                    "lesson_date": ld.isoformat(),
                    "topic": lesson.topic,
                    "description": lesson.topic or "",
                })

    return materials
