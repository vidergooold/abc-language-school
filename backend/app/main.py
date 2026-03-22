from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import init_db
from app.api.v1 import auth, users, forms, courses, enrollments, news


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы в базе данных при запуске
    await init_db()
    yield


app = FastAPI(
    title="ABC Language School API",
    description="API для школы иностранных языков",
    version="1.0.0",
    lifespan=lifespan,
)

# Разрешаем запросы с фронтенда (Vue.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры с префиксом /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(forms.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")


@app.get("/")
async def root():
    # Корневой маршрут для проверки работы сервера
    return {"message": "ABC Language School API работает"}
