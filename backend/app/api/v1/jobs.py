from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/")
@router.get("")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT * FROM job_vacancies"))
    except (OperationalError, ProgrammingError):
        return []
    return [dict(row) for row in result.mappings().all()]
