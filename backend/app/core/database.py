import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env file")

_SSL_MODE = os.getenv("DB_SSL_MODE", "require").lower()
if _SSL_MODE == "disable":
    _ssl_connect_args = {}
elif _SSL_MODE == "require":
    _ssl_connect_args = {"ssl": "require"}
else:
    _ssl_connect_args = {"ssl": "require"}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=_ssl_connect_args)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
