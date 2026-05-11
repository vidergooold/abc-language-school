#!/bin/bash
set -e
echo "Starting server..."
echo "Running database migrations..."
alembic upgrade head
echo "Seeding branches..."
python seed_branches_22.py
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
