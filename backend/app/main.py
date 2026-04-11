from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.api.v1 import (
    auth, users, courses, enrollments,
    news, groups, schedule,
    payments, attendance, notifications,
    waitlist, analytics,
)

# Роутеры отключены до создания недостающих моделей:
# forms, teachers, reports, audit, discounts
# Временно отключен: scheduler, audit_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ABC Language School API",
    description=(
        "API для языковой школы ABC.\n\n"
        "Модули: авторизация, новости (с отложенной публикацией), "
        "расписание (проверка конфликтов), группы и курсы, "
        "посещаемость, финансы и аналитика, "
        "лист ожидания, уведомления."
    ),
    version="4.0.0",
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Роутеры ───────────────────────────────────────────────────────────────────
app.include_router(auth.router,          prefix="/api/v1")
app.include_router(users.router,         prefix="/api/v1")
app.include_router(courses.router,       prefix="/api/v1")
app.include_router(enrollments.router,   prefix="/api/v1")
app.include_router(news.router,          prefix="/api/v1")
app.include_router(groups.router,        prefix="/api/v1")
app.include_router(schedule.router,      prefix="/api/v1")
app.include_router(payments.router,      prefix="/api/v1")
app.include_router(attendance.router,    prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(waitlist.router,      prefix="/api/v1")
app.include_router(analytics.router,     prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "ABC Language School API v4.0 работает"}
