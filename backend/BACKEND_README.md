# ABC Language School — Backend

FastAPI backend for the ABC Language School management system. Handles authentication, scheduling, attendance, payments, notifications, and analytics.

## Deployment Infrastructure

- **Backend**: Railway (start command: `entrypoint.sh` → `uvicorn app.main:app`)
- **Database**: Railway PostgreSQL plugin (`sslmode=require`; no custom CA needed)
- **Frontend**: Vercel (see root `README.md`)

---

## Installation

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set environment variables

Copy the root `.env.example` to `.env` and fill in all values. The backend reads the following variables at startup:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection URL (Railway sets this automatically). Use the `postgresql+asyncpg://...` scheme — Alembic's `env.py` strips the driver prefix automatically when running migrations. |
| `SECRET_KEY` | ✅ | JWT signing secret. Backend raises `RuntimeError` at startup if missing. |
| `ALGORITHM` | optional | JWT algorithm (default: `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | optional | Token lifetime in minutes (default: `480`). |
| `APP_BASE_URL` | optional | Public backend URL used by the APScheduler for internal HTTP calls. Logs a warning if unset. |
| `ALLOWED_ORIGINS` | optional | Comma-separated list of allowed CORS origins (e.g. `https://abc-school-frontend.vercel.app`). Takes precedence over `FRONTEND_URL`. |
| `FRONTEND_URL` | optional | Legacy CORS origin alias. Use `ALLOWED_ORIGINS` instead. Defaults to `localhost:5173`, `localhost:3000` if neither is set. |
| `ADMIN_EMAIL` | optional | Admin account email created by seed scripts. |
| `ADMIN_PASSWORD` | optional | Admin account password. |
| `MIGRATION_KEY` | optional | Secret header for the `POST /api/v1/admin/run-migrations` endpoint. |
| `SMTP_SERVER` | optional | SMTP host for outgoing email. |
| `SMTP_PORT` | optional | SMTP port. |
| `SMTP_USERNAME` | optional | SMTP login. |
| `SMTP_PASSWORD` | optional | SMTP app password. |

### 3. Run database migrations

```bash
alembic upgrade head
```

Alembic reads `DATABASE_URL` from the environment and applies all migration files in `alembic/versions/` in order.

### 4. Seed the database

```bash
# All-in-one (recommended):
python seeds/seed_all.py

# Or step by step:
python seed_real_schedule.py   # Step 1 — users, groups, schedule
python seed_student_groups.py  # Step 2 — populate student_groups (fixes attendance matrix)
```

`seed_student_groups.py` is idempotent — safe to run multiple times.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

API available at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

---

## API Authentication

All protected endpoints require a **JWT Bearer token** in the `Authorization` header:

```
Authorization: Bearer <token>
```

Obtain a token by posting credentials to `POST /api/v1/auth/login`:

```json
{
  "username": "user@example.com",
  "password": "secret"
}
```

Response includes `access_token` and `token_type: "bearer"`. Token lifetime is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES` (default 480 minutes).

Three roles are supported: `student`, `teacher`, `admin`. Admin-only endpoints return `403 Forbidden` for lower roles.

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # Deployed entrypoint (v1.2.0, APScheduler)
│   ├── core/
│   │   ├── database.py      # Async SQLAlchemy engine + session
│   │   ├── security.py      # JWT helpers, password hashing
│   │   ├── cors.py          # CORS origins from ALLOWED_ORIGINS env var
│   │   └── scheduler.py     # APScheduler setup
│   ├── models/              # SQLAlchemy ORM models
│   └── api/
│       └── v1/              # All API routers
├── alembic/                 # Alembic migration environment
│   └── versions/            # Migration files
├── seeds/
│   └── seed_all.py          # Canonical all-in-one seed
├── entrypoint.sh            # Railway start command
└── requirements.txt
```

---

## Running Tests

```bash
pytest backend/tests -q
```

The test suite bootstraps `DATABASE_URL` and `SECRET_KEY` defaults in `backend/tests/conftest.py` so import-only smoke checks work without a live database.
