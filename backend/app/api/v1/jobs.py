from fastapi import APIRouter, Depends
from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
async def get_jobs(db: AsyncSession = Depends(get_db)):
    try:
        def _load_job_vacancies(sync_session):
            bind = sync_session.get_bind()
            return Table("job_vacancies", MetaData(), autoload_with=bind)

        job_vacancies = await db.run_sync(_load_job_vacancies)
        result = await db.execute(select(job_vacancies))
    except NoSuchTableError:
        return []
    return [dict(row) for row in result.mappings().all()]
