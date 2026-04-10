from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.api.v1 import (
    auth, users, forms, courses, enrollments,
    news, teachers, groups, schedule,
    payments, attendance, notifications, audit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ABC Language School API",
    description="API для школы иностранных языков",
    version="2.0.0",
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
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(forms.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")

# ─── Новости с логикой статусов ──────────────────────────────────────
app.include_router(news.router, prefix="/api/v1")

# ─── Преподаватели ───────────────────────────────────────────────────
app.include_router(teachers.router, prefix="/api/v1")

# ─── Курсы, группы, студенты в группах ──────────────────────────────
app.include_router(groups.router, prefix="/api/v1")

# ─── Расписание с проверкой конфликтов ──────────────────────────────
app.include_router(schedule.router, prefix="/api/v1")

# ─── Финансы: счета, оплаты, аналитика ──────────────────────────────
app.include_router(payments.router, prefix="/api/v1")

# ─── Посещаемость ────────────────────────────────────────────────────
app.include_router(attendance.router, prefix="/api/v1")

# ─── Уведомления и очередь рассылок ─────────────────────────────────
app.include_router(notifications.router, prefix="/api/v1")

# ─── Журнал действий (аудит) ─────────────────────────────────────────
app.include_router(audit.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "ABC Language School API v2.0 работает"}
