import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import DeclarativeBase
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Определяем свой Base — не трогаем database.py вообще
class Base(DeclarativeBase):
    pass

# Патчим database модуль ДО импорта моделей
import sys
from unittest.mock import MagicMock

# Создаём фейковый database модуль
mock_db = MagicMock()
mock_db.Base = Base
sys.modules['app.core.database'] = mock_db

# Теперь импортируем все модели — они зарегистрируются на нашем Base
import app.models  # noqa: F401

target_metadata = Base.metadata


def get_url():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    # Приводим к синхронному postgresql:// для alembic
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgresql+psycopg2://", "postgresql://")
    url = url.replace("postgres://", "postgresql://")
    return url


def run_migrations_offline():
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
