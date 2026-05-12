#!/bin/bash
set -e
echo "Starting server..."
echo "Running database migrations..."
alembic upgrade head
echo "Checking branches.is_administrative column..."
if ! python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def check():
    url = os.environ['DATABASE_URL'].replace(
        'postgres://', 'postgresql+asyncpg://')
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        await conn.execute(
            text('SELECT is_administrative FROM branches LIMIT 1'))
    await engine.dispose()
    print('OK: is_administrative column exists')
asyncio.run(check())
"; then
  echo "ERROR: branches.is_administrative column check failed"
  exit 1
fi
echo "Seeding branches..."
python seed_branches_22.py
echo "Seeding account data..."
python seed_account_data.py
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
