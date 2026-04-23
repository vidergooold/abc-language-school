from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db

# Импортируем все модели чтобы Base.metadata знал о всех таблицах
from app.models import user, news  # noqa: F401
from app.models.forms import ApplicationForm, StudentProfile  # noqa: F401
from app.models.enrollment import Enrollment  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.schedule import Lesson, Classroom  # noqa: F401
from app.models.attendance import Attendance  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.group import Group  # noqa: F401

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
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ABC Language School API",
    description="""
    REST API для сайта языковой школы **ABC Language School** (г. Новосибирск).

    ## Возможности
    - 🔐 Аутентификация пользователей (JWT)
    - 📚 Управление курсами
    - 📰 Новости и объявления
    - 📝 Запись на курсы
    - 👤 Личный кабинет ученика
    - 📂 Документы и договоры
    - 🗓 Расписание занятий
    - ✅ Посещаемость
    - 💳 Оплата
    - 🔔 Уведомления
    """,
    version="1.1.0",
    contact={
        "name": "ABC Language School",
        "email": "info@abc-school.ru",
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Авторизация
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

# Общедоступные ресурсы
app.include_router(courses.router, prefix="/api/v1")
app.include_router(news_router.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")
app.include_router(forms.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")

# Личный кабинет / начальник / преподаватель
app.include_router(scheduler.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(groups.router, prefix="/api/v1")

# Админ
app.include_router(admin.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "project": "ABC Language School",
        "version": "1.1.0",
        "docs": "/docs",
        "status": "running"
    }
