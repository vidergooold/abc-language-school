from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.core.scheduler import setup_scheduler, scheduler
from app.api.v1 import (
    auth, users, forms, courses, enrollments,
    news, teachers, groups, schedule,
    payments, attendance, notifications, audit,
)
from app.api.v1 import waitlist, analytics, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    setup_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="ABC Language School API",
    description=(
        "API для языковой школы ABC.\n\n"
        "Модули: авторизация, новости (с отложенной публикацией), "
        "расписание (проверка конфликтов), группы и курсы, "
        "посещаемость, финансы и аналитика, "
        "лист ожидания, отчёты с кэшированием, "
        "уведомления и очередь рассылок, планировщик APScheduler, аудит."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Базовые роуты ───────────────────────────────────────────────────
app.include_router(auth.router,        prefix="/api/v1")
app.include_router(users.router,       prefix="/api/v1")
app.include_router(forms.router,       prefix="/api/v1")
app.include_router(courses.router,     prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")

# ─── Новости с логикой статусов и отложенной публикацией ─────────────
app.include_router(news.router,        prefix="/api/v1")

# ─── Преподаватели ───────────────────────────────────────────────────
app.include_router(teachers.router,    prefix="/api/v1")

# ─── Курсы, группы, студенты в группах ──────────────────────────────
app.include_router(groups.router,      prefix="/api/v1")

# ─── Расписание с проверкой трёх видов конфликтов ───────────────────
app.include_router(schedule.router,    prefix="/api/v1")

# ─── Финансы: счета, оплаты, аналитика ──────────────────────────────
app.include_router(payments.router,    prefix="/api/v1")

# ─── Посещаемость ────────────────────────────────────────────────────
app.include_router(attendance.router,  prefix="/api/v1")

# ─── Уведомления и очередь рассылок ─────────────────────────────────
app.include_router(notifications.router, prefix="/api/v1")

# ─── Журнал действий (аудит) ─────────────────────────────────────────
app.include_router(audit.router,       prefix="/api/v1")

# ─── Лист ожидания ───────────────────────────────────────────────────
app.include_router(waitlist.router,    prefix="/api/v1")

# ─── Расширенная аналитика: unit-economics, BEP, сценарии ───────────
app.include_router(analytics.router,   prefix="/api/v1")

# ─── Отчёты с кэшированием ───────────────────────────────────────────
app.include_router(reports.router,     prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "ABC Language School API v3.0 работает"}


@app.get("/api/v1/scheduler/status")
async def scheduler_status():
    """Статус планировщика и список активных задач."""
    jobs = [
        {
            "id":       job.id,
            "name":     job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }
        for job in scheduler.get_jobs()
    ]
    return {"running": scheduler.running, "jobs": jobs}
