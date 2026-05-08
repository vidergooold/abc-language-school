# ABC Language School

Web-based management system for ABC Language School (Novosibirsk). Handles course enrollment, scheduling, attendance tracking, payments, notifications, and economic analytics.

## Tech Stack

| Layer | Technology | Hosting |
|-------|-----------|---------|
| Frontend | Vue 3 + TypeScript (Vite) | Vercel |
| Backend | FastAPI + Python 3.9+ | Railway |
| Database | PostgreSQL | Railway PostgreSQL plugin |
| ORM | SQLAlchemy (async) + Alembic | — |

---

## Local Development

### Prerequisites
- Docker + Docker Compose
- Node.js 18+
- Python 3.9+

### 1. Clone the repository

```bash
git clone https://github.com/vidergooold/abc-language-school.git
cd abc-language-school
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in all required values
```

### 3. Start all services with Docker Compose

```bash
docker-compose up
```

This starts PostgreSQL on port 5432, the backend on port 8000, and the frontend on port 3000.

### 4. Frontend (standalone)

```bash
cd frontend
npm install
npm run dev
```

Starts the Vite dev server at http://localhost:5173.

### 5. Backend (standalone)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Starts the FastAPI server at http://localhost:8000. Interactive docs available at http://localhost:8000/docs.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values listed below.

### Backend (Railway)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL (Railway fills this automatically). Example: `postgresql://user:pass@host:5432/dbname?sslmode=require` |
| `SECRET_KEY` | Secret key used to sign JWT tokens. **Required** — backend raises `RuntimeError` on startup if missing. |
| `ALGORITHM` | JWT signing algorithm (default: `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes (default: `480`). |
| `APP_BASE_URL` | Public URL of the deployed backend, used by the internal scheduler (e.g. `https://your-app.railway.app`). |
| `FRONTEND_URL` | Frontend origin for CORS (e.g. `https://abc-school-frontend.vercel.app`). Falls back to `localhost:5173` / `localhost:3000` if not set. |
| `ADMIN_EMAIL` | Email for the initial admin account created by seed scripts. |
| `ADMIN_PASSWORD` | Password for the initial admin account. |
| `MIGRATION_KEY` | Secret header value that protects the `POST /api/v1/admin/run-migrations` endpoint. |
| `SMTP_SERVER` | SMTP host for outgoing email (e.g. `smtp.gmail.com`). |
| `SMTP_PORT` | SMTP port (e.g. `587`). |
| `SMTP_USERNAME` | SMTP login address. |
| `SMTP_PASSWORD` | SMTP app password. |

### Frontend (Vercel)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Public URL of the backend API (e.g. `https://your-app.railway.app`). Set in Vercel → Settings → Environment Variables. |

---

## Seed Scripts

Run all seed scripts from the `backend/` directory.

### Option A — all-in-one (recommended)

```bash
cd backend
python seeds/seed_all.py
```

Runs the full seed pipeline: demo data, real schedule, and student_groups population.

### Option B — step by step

**Step 1** — main seed (users, groups, schedule):

```bash
cd backend
python seed_real_schedule.py
```

**Step 2** — fix attendance matrix (run after step 1):

```bash
cd backend
python seed_student_groups.py
```

`seed_student_groups.py` populates the `student_groups` table for all groups and fixes the empty attendance matrix ("No active students in this group"). The script is idempotent — safe to run multiple times.

---

## User Roles

| Role | Access |
|------|--------|
| `student` | Personal account: view schedule, attendance, payments, homework, documents, enroll in courses |
| `teacher` | Schedule management, attendance marking, homework assignment, group view |
| `admin` | Full access: all of the above + user management, analytics, audit log, notifications, reports |

---

## API Overview

All endpoints are served under the `/api/v1` prefix. Interactive docs: `/docs`.

| Router | Prefix | Description |
|--------|--------|-------------|
| `auth` | `/api/v1/auth` | Registration, login, JWT token issuance |
| `users` | `/api/v1` | User profile CRUD (admin manages staff accounts) |
| `courses` | `/api/v1` | Course catalogue |
| `news` | `/api/v1` | News and announcements |
| `enrollments` | `/api/v1/enrollments` | Course enrollment management |
| `forms` | `/api/v1/forms` | Application forms (child, adult, preschool, teacher, etc.) |
| `documents` | `/api/v1` | Student documents and contracts |
| `branches` | `/api/v1/branches` | School branch locations |
| `programs` | `/api/v1/programs` | Educational programs |
| `scheduler` | `/api/v1` | Lesson schedule with conflict prevention |
| `attendance` | `/api/v1/attendance` | Attendance records and grades |
| `payments` | `/api/v1` | Payment tracking |
| `notifications` | `/api/v1/notifications` | Notification queue management |
| `groups` | `/api/v1` | Course groups and student membership |
| `teachers` | `/api/v1/teachers` | Teacher profiles |
| `students` | `/api/v1/students` | Student profiles |
| `homeworks` | `/api/v1/homeworks` | Homework assignments |
| `messages` | `/api/v1/messages` | Internal messaging |
| `reports` | `/api/v1/reports` | Cached analytics reports |
| `admin` | `/api/v1/admin` | Admin: user management, migrations endpoint |
| `analytics` | `/api/v1/analytics` | Revenue reports, break-even, teacher load |
| `audit` | `/api/v1/audit` | Audit log |

---

## Deployment

### Frontend — Vercel

1. Connect the GitHub repository to Vercel.
2. Set the root directory to `frontend`.
3. Add the `VITE_API_URL` environment variable pointing to the Railway backend URL.
4. Vercel builds and deploys automatically on every push to `main`.

### Backend + Database — Railway

1. Create a new Railway project and add a **PostgreSQL** plugin — Railway populates `DATABASE_URL` automatically.
2. Deploy the `backend/` directory; Railway uses `entrypoint.sh` as the start command.
3. Set all required environment variables listed in the **Environment Variables** section above.
4. Run database migrations after the first deploy:

```bash
# Via the migrations endpoint (requires MIGRATION_KEY header):
curl -X POST https://your-app.railway.app/api/v1/admin/run-migrations \
     -H "x-migration-key: <MIGRATION_KEY>"

# Or directly from a Railway shell:
alembic upgrade head
```
