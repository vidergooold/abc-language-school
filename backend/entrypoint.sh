#!/bin/bash
set -e
echo "Running migrations..."
# Используем psycopg2 для миграций (синхронный драйвер)
ALEMBIC_URL=$(echo $DATABASE_URL | sed 's/postgresql+asyncpg/postgresql+psycopg2/g' | sed 's/?.*$//')
export DATABASE_URL=$ALEMBIC_URL
alembic upgrade head
echo "Migrations complete. Starting server..."
# Восстанавливаем оригинальный URL для uvicorn
export DATABASE_URL="postgresql+asyncpg://abc_user:AbcSchool2026!@rc1b-hdbhrmnd0e18v14r.mdb.yandexcloud.net/abc_school"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
