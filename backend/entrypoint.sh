#!/bin/bash
set -e
echo "Running migrations..."
ORIGINAL_URL="$DATABASE_URL"
PSYCOPG2_URL=$(echo "$DATABASE_URL" | sed 's/postgresql+asyncpg/postgresql+psycopg2/' | sed 's/?.*$//')
DATABASE_URL="$PSYCOPG2_URL" alembic upgrade head
echo "Migrations complete. Starting server..."
export DATABASE_URL="$ORIGINAL_URL"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
