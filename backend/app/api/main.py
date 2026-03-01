from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api.v1 import auth, users, courses, news, enrollments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="ABC Language School API",
    description="REST API для сайта языковой школы ABC. Управление курсами, новостями, записями и пользователями.",
    version="1.0.0",
    contact={
        "name": "ABC Language School",
        "email": "info@abc-school.ru",
    },
    license_info={
        "name": "MIT",
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

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(enrollments.router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "project": "ABC Language School",
        "api_version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }
