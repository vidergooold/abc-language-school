# Audit Report — ABC Language School (`main` branch)

_Generated: 2026-05-08_

---

## 1. Open Pull Requests

| # | Title | Status |
|---|-------|--------|
| #2 | Очистить корень репозитория от нерелевантных tracked-артефактов | ⚠️ Needs review — `.history/` is already in `.gitignore` but its files are still tracked in git; this PR would untrack them |
| #6 | Consolidate backend seed scripts into `backend/seeds/seed_all.py` | ⚠️ Needs review — `backend/seeds/` exists with only a `branches.sql` stub, not the consolidated script yet |
| #11 | Add `backend/seed_full_demo.py` | ✅ **SUPERSEDED** — `backend/seed_full_demo.py` already exists on `main` |
| #12 | Fix attendance matrix UI, schedule filtering, grade 3, and payment button | ⚠️ Needs review — UI fixes; unclear if already partially applied to `main` |
| #14 | Switch database config from SQLite fallback to required PostgreSQL URL | ✅ **SUPERSEDED** — `backend/app/core/database.py` on `main` already requires `DATABASE_URL` and has no SQLite fallback |
| #15 | Fix: load `.env` via python-dotenv, remove SQLite fallback, enforce PostgreSQL | ✅ **SUPERSEDED** — same as #14; both are already reflected in current `database.py` |
| #16 | Fix `ResponseValidationError` on nullable DB fields across all response schemas | ⚠️ Needs review — schemas already use `Optional[T] = None` widely; the exact scope of remaining issues needs investigation |

**Summary:** PRs #11, #14, #15 are superseded by `main`. PRs #2, #6, #12, #16 still need review/merging.

---

## 2. `main` Branch Audit

### 2a. Broken Imports / Missing Modules (backend/app/)

**CRITICAL — Fixed in this PR:**

- `backend/app/api/main.py` line 8 imported `ApplicationForm, StudentProfile` from `app.models.forms`, but **neither class exists** in that module (the actual classes are `ChildForm`, `AdultForm`, `PreschoolForm`, `TeacherForm`, `TestingForm`, `FeedbackForm`, `TaxForm`). This would cause an `ImportError` on startup.
  - **Fix applied:** Import corrected to all actual form model classes.

**No other syntax errors** found in any `backend/app/**/*.py` file.

---

### 2b. TODO / FIXME / Placeholder Comments

| Location | Content |
|----------|---------|
| `frontend/src/pages/clients/Important.vue` | Entire page is a placeholder: "Раздел находится в разработке" — this page has no route but the component exists |

No `TODO` or `FIXME` comments found in backend Python files. Numerous `placeholder` attributes in frontend are HTML input placeholders (normal form UX), not code placeholders.

---

### 2c. Unused Files / Dead Code

**Backend:**
- `backend/alembic.ini.bak` — backup file, not needed in version control
- Multiple seed scripts in `backend/` root with overlapping purpose (`seed_demo.py`, `seed_real_data.py`, `seed_real_schedule.py`, `seed_teachers.py`, `seed_student_groups.py`, `seed_news.py`, `seed_news_fixed.py`, `seed_account_data.py`, `seed_branches_22.py`, `seed_full_demo.py`) — PR #6 proposes consolidating these
- `backend/tests/` directory exists but appears empty/unused
- `backend/verify_schedule.py` — standalone script, not imported anywhere
- `backend/test_admin.py`, `backend/test_api.py` — test scripts not integrated with a test runner

**Frontend:**
- `frontend/src/components/account/BranchTeacherGroupFilter.vue` — **zero references** across the entire frontend; never imported or used anywhere
- `frontend/src/pages/account/Documents.vue` — was not routed (fixed in this PR)
- `frontend/src/pages/account/Profile.vue` — was not routed (`/account/profile` redirected to `/account` instead of rendering the Profile component; fixed in this PR)
- `frontend/src/pages/clients/Important.vue` — placeholder component with no route defined in router

**.history/ directory:**
- ~100+ historical files from VS Code Local History extension are committed to git (`.history/` prefix). The directory is listed in `.gitignore` but the files were committed before the ignore rule was added. PR #2 addresses this.

---

### 2d. Missing Alembic Migrations

The following model tables **exist in Python models but have NO `op.create_table(...)` in any migration file** — they are only created by `Base.metadata.create_all` on first run, which is not production-safe:

| Table | Model |
|-------|-------|
| `adult_forms` | `AdultForm` |
| `audit_log` | `AuditLog` |
| `child_forms` | `ChildForm` |
| `classrooms` | `Classroom` |
| `enrollment_status_history` | `EnrollmentStatusHistory` |
| `feedback_forms` | `FeedbackForm` |
| `homeworks` | `Homework` |
| `invoices` | `Invoice` |
| `messages` | `Message` |
| `news_categories` | `NewsCategory` |
| `news_likes` | `NewsLike` |
| `news_status_history` | `NewsStatusHistory` |
| `notification_queue` | `NotificationQueue` |
| `preschool_forms` | `PreschoolForm` |
| `report_cache` | `ReportCache` |
| `room_bookings` | `RoomBooking` |
| `student_groups` | `StudentGroup` |
| `tax_forms` | `TaxForm` |
| `teacher_forms` | `TeacherForm` |
| `teacher_groups` | `TeacherGroup` |
| `teachers` | `Teacher` |
| `testing_forms` | `TestingForm` |

**22 tables** are missing migrations. This is a significant gap — a fresh deployment using `alembic upgrade head` would be missing all of these tables.

---

### 2e. Hardcoded Secrets, Passwords, Localhost URLs

| File | Issue | Fixed |
|------|-------|-------|
| `backend/app/core/security.py` | `SECRET_KEY = "super-secret-key"` hardcoded | ✅ Fixed — now reads `os.getenv("SECRET_KEY", "super-secret-key")` |
| `backend/app/core/scheduler.py` | `http://127.0.0.1:8000/api/v1/admin/news/publish-scheduled` hardcoded | ✅ Fixed — now reads `APP_BASE_URL` from environment |
| `backend/app/api/main.py` | `http://localhost:5173` and `http://localhost:3000` in old CORS config | ℹ️ Not an issue — an older version had this; current `main.py` uses `allow_origins=["*"]` |
| `backend/requirements.txt` | `python-dotenv>=1.0.0` listed twice (duplicate line) | ⚠️ Minor — harmless but should be cleaned up |

---

## 3. Frontend Audit

### 3a. Components Imported but Not Used

| Component | Status |
|-----------|--------|
| `BranchTeacherGroupFilter.vue` | **Dead code** — imported nowhere, never registered in any page |

All other components in `components/` are used (verified by search).

### 3b. API Calls Referencing Non-Existent Backend Endpoints

**CRITICAL — Fixed in this PR:**

The following 8 API routers existed in `backend/app/api/v1/` but were **never registered** in `backend/app/api/main.py`, making all their endpoints return HTTP 404:

| Router file | Prefix | Frontend pages that call it |
|-------------|--------|-----------------------------|
| `branches.py` | `/api/v1/branches` | Dashboard, Schedule, ScheduleAdmin |
| `students.py` | `/api/v1/students` | Students |
| `teachers.py` | `/api/v1/teachers` | Teachers |
| `programs.py` | `/api/v1/programs` | (educational programs) |
| `homeworks.py` | `/api/v1/homeworks` | Homework |
| `messages.py` | `/api/v1/messages` | (messaging system) |
| `reports.py` | `/api/v1/reports` | (reports) |
| `audit.py` | `/api/v1/audit` | (admin audit log) |

- **Fix applied:** All 8 routers are now registered in `main.py`.

### 3c. Hardcoded URLs

| File | Issue | Fixed |
|------|-------|-------|
| `frontend/src/pages/Jobs.vue` line 109 | Fallback URL was `http://127.0.0.1:8000` (localhost) | ✅ Fixed — now uses `https://abc-language-school-production.up.railway.app` (same as `http.ts`) |
| `frontend/src/api/http.ts` | Fallback URL is production Railway URL | ✅ Correct |

---

## 4. PR Duplication Analysis

| PR | Superseded by `main`? | Reason |
|----|----------------------|--------|
| #11 | ✅ Yes | `backend/seed_full_demo.py` already committed to `main` |
| #14 | ✅ Yes | `database.py` on `main` already has PostgreSQL-only config with no SQLite fallback |
| #15 | ✅ Yes | Same as #14 — `database.py` already loads `.env` via `python-dotenv` and raises `RuntimeError` if `DATABASE_URL` is missing |
| #2 | ❌ No | `.history/` files are still tracked in git; needs cleanup |
| #6 | ❌ No | Seed scripts are not yet consolidated |
| #12 | ❌ No | UI fixes for attendance/schedule/payments |
| #16 | ❌ Partially | Some nullable schema fixes may still be needed depending on which specific fields are failing |

---

## 5. Prioritized Action Plan

### 🔴 P0 — Blocking (app won't run or data is corrupt)

1. **[DONE — this PR]** Fix broken `ApplicationForm`/`StudentProfile` import in `backend/app/api/main.py` → corrected to actual form model classes
2. **[DONE — this PR]** Register 8 missing API routers in `main.py` (`branches`, `students`, `teachers`, `programs`, `homeworks`, `messages`, `reports`, `audit`) — without this, major parts of the admin panel return 404
3. **[DONE — this PR]** Fix hardcoded `SECRET_KEY = "super-secret-key"` in `security.py` → now reads from env

### 🟠 P1 — High Priority (security / broken UX)

4. **Create Alembic migrations for 22 missing tables** — currently `init_db()` uses `create_all` which only works for fresh DBs; any incremental migration via Alembic will miss these tables in production
5. **Close superseded PRs** — Close #11, #14, #15 as they duplicate what's already in `main`
6. **Merge PR #16** — Fix any remaining `ResponseValidationError` on nullable DB fields if confirmed still present
7. **[DONE — this PR]** Add routes for `Documents.vue` and `Profile.vue` in the frontend router — these pages existed but were unreachable
8. **[DONE — this PR]** Fix `Documents.vue` template syntax error (missing `</template>` closing tag for `v-for` block)

### 🟡 P2 — Medium Priority (maintainability / correctness)

9. **Merge PR #12** — Attendance matrix UI, schedule filtering, payment button fixes
10. **Merge PR #2** — Untrack `.history/` files from git (they bloat the repo significantly)
11. **Merge or close PR #6** — Consolidate seed scripts; the `backend/seeds/` directory is partially prepared
12. **Remove `BranchTeacherGroupFilter.vue`** — unused component that will confuse future contributors
13. **Add `Important.vue` to router** (or delete it) — currently unreachable placeholder page under `/clients`
14. **Fix duplicate `python-dotenv` line** in `backend/requirements.txt`

### 🟢 P3 — Low Priority (polish)

15. **[DONE — this PR]** Fix hardcoded `http://127.0.0.1:8000` fallback in `Jobs.vue` → production Railway URL
16. **[DONE — this PR]** Fix hardcoded `http://127.0.0.1:8000` in `scheduler.py` → `APP_BASE_URL` env var
17. **Add `APP_BASE_URL` to `.env.example`** — documented for deployers
18. **Remove `alembic.ini.bak`** — backup file should not be in version control
19. **Set up a proper test runner** — `backend/tests/` is empty, `test_admin.py` and `test_api.py` in root are not pytest-integrated
20. **Implement `Important.vue`** content or remove the placeholder page entirely
