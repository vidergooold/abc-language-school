import logging
import os
import secrets
import subprocess
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler, shutdown_scheduler

# Импортируем все модели чтобы Base.metadata знал о всех таблицах
from app.models import user, news  # noqa: F401
from app.models.forms import (  # noqa: F401
    ChildForm, AdultForm, PreschoolForm,
    TeacherForm, TestingForm, FeedbackForm, TaxForm,
)
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.branch import Branch  # noqa: F401
from app.models.educational_program import EducationalProgram  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.schedule import Lesson, Classroom  # noqa: F401
from app.models.attendance import Attendance  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.group import Group  # noqa: F401
from app.models.homework import Homework  # noqa: F401
from app.models.teacher import Teacher, TeacherGroup  # noqa: F401
from app.models.message import Message  # noqa: F401

from app.api.v1 import (
    auth,
    users,
    courses,
    news as news_router,
    enrollments,
    forms,
    documents,
    scheduler,
    attendance,
    payments,
    notifications,
    groups,
    admin,
    analytics,
    teachers,
    jobs,
    applications,
)
from app.api.v1 import branches, programs, students, homeworks, audit, reports, messages
from app.core.cors import get_cors_origins

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError) as exc:
        logger.warning(
            "Failed to reconfigure stdout to UTF-8 (%s); continuing with system default encoding",
            type(exc).__name__,
            exc_info=True,
        )
    start_scheduler()
    yield
    shutdown_scheduler()


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"


app = FastAPI(
    title="ABC Language School API",
    description="""
    REST API для сайта языковой школы **ABC Language School** (г. Новосибирск).

    ## Возможности
    - 🔐 Аутентификация (JWT)
    - 📚 Курсы и группы
    - 📰 Новости и объявления
    - 📝 Запись на курсы
    - 👤 Личный кабинет
    - 📂 Документы и договоры
    - 🗓 Расписание занятий
    - ✅ Посещаемость
    - 💳 Оплата
    - 🔔 Уведомления
    - 🏫 Филиалы и образовательные программы
    - 🎓 База студентов
    """,
    version="1.2.0",
    contact={
        "name": "ABC Language School",
        "email": "info@abc-school.ru",
    },
    lifespan=lifespan,
    default_response_class=UTF8JSONResponse,
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
        allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Авторизация
app.include_router(auth.router,          prefix="/api/v1")
app.include_router(users.router,         prefix="/api/v1")

# Общедоступные ресурсы
app.include_router(courses.router,       prefix="/api/v1")
app.include_router(jobs.router,          prefix="/api/v1")
app.include_router(news_router.router,   prefix="/api/v1")
app.include_router(enrollments.router,   prefix="/api/v1")
app.include_router(forms.router,         prefix="/api/v1")
app.include_router(documents.router,     prefix="/api/v1")
app.include_router(branches.router,      prefix="/api/v1")
app.include_router(programs.router,      prefix="/api/v1")

# Личный кабинет / преподаватель
app.include_router(scheduler.router,     prefix="/api/v1")
app.include_router(attendance.router,    prefix="/api/v1")
app.include_router(payments.router,      prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(groups.router,        prefix="/api/v1")
app.include_router(teachers.router,      prefix="/api/v1")
app.include_router(applications.router,  prefix="/api/v1")
app.include_router(students.router,      prefix="/api/v1")
app.include_router(homeworks.router,     prefix="/api/v1")

# Админ
app.include_router(admin.router,         prefix="/api/v1")
app.include_router(analytics.router,     prefix="/api/v1")
app.include_router(audit.router,         prefix="/api/v1")
app.include_router(reports.router,       prefix="/api/v1")
app.include_router(messages.router,      prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "project": "ABC Language School",
        "version": "1.2.0",
        "docs": "/docs",
        "status": "running",
    }


@app.post("/api/v1/admin/run-migrations", tags=["admin"])
def run_migrations(x_migration_key: str = Header(...)):
    migration_key = os.environ.get("MIGRATION_KEY")
    if not migration_key or not secrets.compare_digest(x_migration_key, migration_key):
        raise HTTPException(status_code=403, detail="Forbidden")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True, text=True, cwd="/app", timeout=120
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
