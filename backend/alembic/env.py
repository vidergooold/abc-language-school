import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Выставляем DATABASE_URL до импорта database.py
# (он уже должен быть в env, но на всякий случай)
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Временно подменяем create_async_engine на заглушку
# чтобы database.py не упал при импорте в синхронном контексте
import sqlalchemy.ext.asyncio as _async_module
_real_create_async_engine = _async_module.create_async_engine

def _fake_async_engine(url, **kwargs):
    class _FakeEngine:
        pass
    return _FakeEngine()

_async_module.create_async_engine = _fake_async_engine

# Теперь безопасно импортируем database.py и модели
from app.core.database import Base  # noqa: E402
import app.models  # noqa: F401, E402

# Восстанавливаем оригинальную функцию
_async_module.create_async_engine = _real_create_async_engine

target_metadata = Base.metadata

def get_url():
    url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    return url.replace("postgresql+asyncpg://", "postgresql://")

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
