# Audit Report — ABC Language School (`main` branch)

_Generated: 2026-05-08 — Live audit performed on branch `copilot/audit-repository-health-check`_

---

## 1. Verification Results

### 1a. Backend

```
SECRET_KEY=dummy DATABASE_URL=postgresql+asyncpg://... python -c "from app.api.main import app"
✅  Backend imports OK — all 23 routers registered, 100+ endpoints exposed
✅  All backend/app/**/*.py files parse without SyntaxError
```

**Routers registered (both `app.main` and `app.api.main`):**
auth, users, courses, news, enrollments, forms, documents, scheduler/schedule, attendance,
payments, notifications, groups, branches, students, teachers, programs, homeworks, messages,
reports, admin, analytics, audit _(all previously-missing routers are now wired)_

### 1b. Frontend

```
npm --prefix frontend ci   →  installed cleanly
npm --prefix frontend run build  →  vue-tsc + vite  →  ✅  267 modules, 0 errors
```

### 1c. Backend Tests

`backend/tests/` contains only `__init__.py` — **no runnable test suite exists.**
`backend/test_admin.py` and `backend/test_api.py` are standalone scripts, not integrated
with pytest. Running `pytest backend/` produces zero tests collected.

### 1d. Alembic Migration Chain

| Revision | Description |
|----------|-------------|
| `e5ef08f40654` | initial schema |
| `55deb8dbe4c5` | add missing news columns |
| `b20e835de97e` | add student role (enum) |
| `347e6146b684` | add student role (enum) |
| `476b21780d50` | merge heads |
| `a1b2c3d4e5f6` | add status/created_at to form tables |
| `c1d2e3f4a5b6` | create news_categories, news_likes, news_status_history |
| `0dc67413e59c` | add branches, educational_programs, students tables |
| `321110387098` | add manager/working_hours to branches |
| `55deb8dbe4c5` | add_student_role |
| `c4d5e6f7a8b9` | add teacher_id to groups |
| `d1e2f3a4b5c6` | create teacher_groups table |
| `e2f3a4b5c6d7` | drop unused tables (expenses, revenue_analytics, rooms, materials, reviews) |
| `9b1c_manual_messages_drop_unused` | create messages, drop waitlist/discounts |
| `a2b3c4d5e6f7` | add lesson_date to homeworks |
| `b3c4d5e6f7a8` | add grade to attendance |
| `f1e2d3c4b5a6` | fix news null defaults |

---

## 2. What Is Working ✅

| Area | Status |
|------|--------|
| Backend startup (imports, router wiring) | ✅ All clean |
| Frontend build (vue-tsc + vite) | ✅ Passes, 0 errors |
| JWT auth — `SECRET_KEY` from env | ✅ Raises `RuntimeError` at startup if not set |
| Scheduler — `APP_BASE_URL` from env | ✅ Warns if unset; no hardcoded localhost |
| Jobs.vue API URL | ✅ Uses production Railway URL as fallback |
| Frontend router — Documents, Profile | ✅ Both pages are routed |
| `.env.example` | ✅ Documents all required env vars |
| `.history/` cleanup | ✅ Removed by merged PR #2 |
| All 8 previously-missing API routers | ✅ Registered in both `main.py` files |
| Alembic env.py | ✅ Uses sync psycopg2 URL, respects `DATABASE_URL` |
| Python syntax (all `backend/app/**/*.py`) | ✅ Zero parse errors |

---

## 3. What Is Broken / At Risk ⚠️

### 3a. 17 Tables Missing Alembic `CREATE TABLE` Migration (P1 — HIGH)

The following tables exist in SQLAlchemy models and are referenced by active routers, but
**no migration file creates them**. They currently exist in deployed databases only because
`Base.metadata.create_all()` was called at some earlier point. A fresh deployment using
`alembic upgrade head` alone will be missing all of them, causing 500 errors at runtime.

| Table | Model file | Has column-only migration? |
|-------|-----------|---------------------------|
| `adult_forms` | `models/forms.py` | ✅ yes (`a1b2c3d4e5f6`) |
| `audit_log` | `models/audit.py` | ❌ none |
| `child_forms` | `models/forms.py` | ✅ yes (`a1b2c3d4e5f6`) |
| `classrooms` | `models/schedule.py` | ❌ none |
| `enrollment_status_history` | `models/enrollment.py` | ❌ none |
| `feedback_forms` | `models/forms.py` | ❌ none |
| `homeworks` | `models/homework.py` | ✅ yes (`a2b3c4d5e6f7`) |
| `invoices` | `models/payment.py` | ❌ none |
| `notification_queue` | `models/notification.py` | ❌ none |
| `preschool_forms` | `models/forms.py` | ✅ yes (`a1b2c3d4e5f6`) |
| `report_cache` | `models/report.py` | ❌ none |
| `room_bookings` | `models/room_booking.py` | ❌ none |
| `student_groups` | `models/student.py` | ❌ none |
| `tax_forms` | `models/forms.py` | ❌ none |
| `teacher_forms` | `models/forms.py` | ✅ yes (`a1b2c3d4e5f6`) |
| `teachers` | `models/teacher.py` | ❌ none |
| `testing_forms` | `models/forms.py` | ❌ none |

**Recommended fix:** Generate `alembic revision --autogenerate -m "add missing tables"` against
a fresh database that has been brought up with only the existing migrations applied (so that
`create_all` was never called). The autogenerate diff will produce the 17 missing `CREATE TABLE`
statements.

### 3b. Duplicate Entrypoint: `app.main` vs `app.api.main` (P2 — MEDIUM)

Two separate FastAPI applications exist in the repository:

| File | Used by | Version | CORS | Scheduler | `init_db()` |
|------|---------|---------|------|-----------|-------------|
| `backend/app/main.py` | `entrypoint.sh` → **deployed** | 1.2.0 | `["*"]` (fixed) | ✅ yes | ❌ no |
| `backend/app/api/main.py` | nothing | 1.1.0 | `["*"]` | ❌ no | ✅ yes |

The deployed version (`app.main`) **does not call `init_db()`** in its lifespan, so
`Base.metadata.create_all()` is never triggered. All table creation must go through Alembic.
The alternative `app.api.main` is unreferenced — it should either be removed or merged into the
primary entrypoint.

### 3c. No Backend Test Suite (P2 — MEDIUM)

`backend/tests/__init__.py` is empty. `pytest backend/` collects 0 tests. The two
standalone scripts (`test_admin.py`, `test_api.py`) require a live server and are not
pytest-compatible. Core business logic (auth, enrollment, attendance, payments) has no
automated coverage.

### 3d. `docker-compose.yml` Hardcodes `SECRET_KEY` (P3 — LOW)

```yaml
SECRET_KEY=super-secret-key
```

Acceptable for local development, but should be noted — developers who copy this for staging
deployments will expose a weak secret. Add a comment in the file to warn against this.

---

## 4. What Is Unused and Can Be Deleted 🗑️

| Path | Reason |
|------|--------|
| `frontend/src/components/account/BranchTeacherGroupFilter.vue` | ✅ **Removed in this PR** — zero imports, never registered |
| `backend/app/api/main.py` | Unused alternative entrypoint; `entrypoint.sh` uses `app.main:app` |
| `backend/test_admin.py` | Standalone script, not in test suite |
| `backend/test_api.py` | Standalone script, not in test suite |
| `backend/verify_schedule.py` | Standalone diagnostic script |
| `backend/seed_demo.py` | Superseded by `backend/seeds/seed_all.py` |
| `backend/seed_real_schedule.py` | Superseded |
| `backend/seed_teachers.py` | Superseded |
| `backend/seed_student_groups.py` | Superseded |
| `backend/seed_account_data.py` | Superseded |
| `backend/seed_branches_22.py` | Superseded |

---

## 5. What Is Incomplete and Needs Implementation 🚧

| Item | Location | Priority |
|------|----------|----------|
| 17 missing `CREATE TABLE` migrations | `backend/alembic/versions/` | 🔴 P1 |
| Backend test suite | `backend/tests/` | 🟠 P2 |
| `Important.vue` page content | `frontend/src/pages/clients/Important.vue` | 🟡 P3 |
| Notification queue processing | `backend/app/api/v1/notifications.py` — queue endpoint exists but no worker | 🟡 P3 |

---

## 6. Fixes Applied in This PR

| Fix | File(s) |
|-----|---------|
| Removed duplicate `python-dotenv` line | `backend/requirements.txt` |
| Fixed CORS: replaced `["*"]` wildcard (invalid with `allow_credentials=True`) with env-driven origins via `FRONTEND_URL`; extracted to shared `app/core/cors.py`; falls back to `localhost:5173` and `localhost:3000` | `backend/app/main.py`, `backend/app/api/main.py`, `backend/app/core/cors.py` (new) |
| Deleted unused `BranchTeacherGroupFilter.vue` | `frontend/src/components/account/` |
| Added `/clients/important` route for `Important.vue` | `frontend/src/router/index.ts` |

---

## 7. Recommended Execution Order to Finish the Project

### 🔴 P0 — Already done (no action needed)
1. ~~Fix broken `ApplicationForm`/`StudentProfile` import in `main.py`~~ _(was on `main`)_
2. ~~Register 8 missing API routers~~ _(was on `main`)_
3. ~~Fix hardcoded `SECRET_KEY`~~ _(was on `main`)_
4. ~~Fix `Documents.vue` and `Profile.vue` not routed~~ _(was on `main`)_
5. ~~Fix hardcoded localhost URLs (`Jobs.vue`, `scheduler.py`)~~ _(was on `main`)_

### 🔴 P1 — Do immediately
6. **Write Alembic `CREATE TABLE` migrations for the 17 missing tables** — run
   `alembic revision --autogenerate -m "add missing tables"` on a clean DB and commit.
   Without this, a fresh Railway/Docker deployment will be missing half the schema.

### 🟠 P2 — Do next sprint
7. **Remove `backend/app/api/main.py`** — consolidate into `app.main`; add `init_db()` call
   to the deployed entrypoint's lifespan so schema sync works as a safety net.
8. **Set up pytest** in `backend/tests/` with at least smoke tests for auth, enrollment, and
   attendance endpoints (use `httpx.AsyncClient` with `app` transport).
9. **Close or merge PR #16** — verify nullable schema `ResponseValidationError` status.
10. **Merge PR #12** — attendance matrix UI / schedule filtering / payment button.

### 🟡 P3 — Polish
11. Remove `backend/test_admin.py`, `backend/test_api.py`, `backend/verify_schedule.py`
    (or convert them to pytest fixtures).
12. Consolidate redundant seed scripts into `backend/seeds/seed_all.py` (PR #6).
13. Implement or stub out `Important.vue` content properly.
14. Add warning comment to `docker-compose.yml` about the hardcoded `SECRET_KEY`.
15. Delete the superseded standalone seed scripts from `backend/` root.
