# Backend Scripts

This folder contains standalone maintenance and development scripts.
All scripts must be run from the `backend/` directory with `DATABASE_URL` set.

## Setup

```bash
cd backend
export DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

## Database initialization (local dev only)

For production, use Alembic migrations:
```bash
alembic upgrade head
```

For local dev when you want to recreate tables without Alembic:
```bash
python init_db.py
```

## Seed scripts

| Script | Description |
|---|---|
| `seed_real_data.py` | Loads a small set of real course data from the school's Excel export |
| `seed_teachers.py` | Creates teacher profiles |
| `seed_student_groups.py` | Creates groups and assigns students to them |
| `seed_account_data.py` | Creates test users (admin, teachers, students) with known passwords |
| `seed_demo.py` | Creates a self-contained demo dataset |
| `seed_full_demo.py` | Extended demo dataset with schedule, payments, and attendance |
| `seed_branches_22.py` | Seeds the 22 school branch locations |
| `seed_real_schedule.py` | Seeds realistic schedule based on real school data |
| `seed_news.py` | Seeds historical news articles from the school website |
| `seeds/branches.sql` | SQL version of branch seed data (psql only) |

### Typical first-time setup order

```bash
python init_db.py              # or: alembic upgrade head
python seed_branches_22.py
python seed_teachers.py
python seed_account_data.py
python seed_real_data.py
python seed_real_schedule.py
```

## Admin tools

| Script | Description |
|---|---|
| `create_admin.py` | Creates or resets the admin account. Uses `ADMIN_EMAIL` / `ADMIN_PASSWORD` env vars |
| `test_admin.py` | Diagnostic script: verifies admin account exists and password hash works |
| `test_api.py` | Smoke-tests key API endpoints against a running app |
| `verify_schedule.py` | Verifies schedule data integrity in the database |

## Notes

- `seed_news_fixed.py` has been removed — it was an obsolete duplicate of `seed_news.py`
- `init_db.py` uses `asyncio` and the async SQLAlchemy engine; do not use sync `create_all` with this project
- Test users created by `seed_account_data.py`: `teacher123` / `student123` — **never use in production**
