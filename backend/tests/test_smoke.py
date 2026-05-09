"""Smoke test suite for the ABC Language School backend API.

Tests verify that all key endpoints are reachable and return correct HTTP
status codes. Uses pytest-asyncio + httpx AsyncClient with FastAPI's ASGI
transport — no real HTTP calls are made to external servers.

Run with:
    python -m pytest backend/tests/test_smoke.py -v
"""
from datetime import datetime, time, timezone
import os
from uuid import uuid4
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ── SQLite in-memory database used only for smoke tests ─────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _create_user_token(
    db_engine,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> str:
    """Insert a user row into the test DB and return a signed JWT for them.

    Accepts role as a plain string so callers do not need to import UserRole.
    """
    from app.models.user import User, UserRole
    from app.core.security import hash_password, create_access_token

    SessionLocal = async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole(role),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return create_access_token(
            {"sub": str(user.id), "email": user.email, "role": user.role.value}
        )


# ── Session-scoped fixtures ──────────────────────────────────────────────────

@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def db_engine():
    """Create an in-memory SQLite engine and apply the full schema once per
    test session.  All models are already registered with Base.metadata
    because importing app.main pulls in every model module."""
    from app.core.database import Base
    import app.main  # noqa: F401 — side-effect: registers all models

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def client(db_engine):
    """AsyncClient wired to the FastAPI ASGI app with get_db overridden to
    use the in-memory SQLite engine."""
    from app.core.database import get_db
    from app.main import app

    SessionLocal = async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def student_token(db_engine):
    """Create a student user in the test DB and return a valid JWT for them."""
    return await _create_user_token(
        db_engine,
        email="student@smoke-tests.example.com",
        password="StudentPass123",
        full_name="Smoke Student",
        role="student",
    )


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def teacher_token(db_engine):
    """Create a teacher user in the test DB and return a valid JWT for them."""
    return await _create_user_token(
        db_engine,
        email="teacher@smoke-tests.example.com",
        password="TeacherPass123",
        full_name="Smoke Teacher",
        role="teacher",
    )


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def admin_token(db_engine):
    """Create an admin user in the test DB and return a valid JWT for them."""
    return await _create_user_token(
        db_engine,
        email="admin@smoke-tests.example.com",
        password="AdminPass123",
        full_name="Smoke Admin",
        role="admin",
    )


# ── Helper ───────────────────────────────────────────────────────────────────

def auth_headers(token: str) -> dict:
    """Return an Authorization header dict for the given JWT."""
    return {"Authorization": f"Bearer {token}"}


async def _seed_progress_group(db_engine) -> int:
    from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus, StudentGroup
    from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
    from app.models.teacher import Teacher

    SessionLocal = async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        unique_suffix = uuid4().hex
        course = Course(
            name="Smoke Progress Course",
            language="English",
            level=CourseLevel.beginner,
            category=CourseCategory.children,
            price_per_month=1000,
        )
        teacher = Teacher(
            full_name="Smoke Progress Teacher",
            email=f"progress-teacher-{unique_suffix}@smoke-tests.example.com",
        )
        classroom = Classroom(name="Smoke Progress Room")
        session.add_all([course, teacher, classroom])
        await session.flush()

        group = Group(
            name="Smoke Progress Group",
            course_id=course.id,
            teacher_id=teacher.id,
            status=GroupStatus.active,
        )
        session.add(group)
        await session.flush()

        session.add(
            StudentGroup(
                group_id=group.id,
                student_name="Smoke Progress Student",
                student_email="progress-student@smoke-tests.example.com",
                student_type="child",
            )
        )
        session.add(
            Lesson(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                day_of_week=DayOfWeek.monday,
                time_start=time(10, 0),
                time_end=time(11, 0),
                status=LessonStatus.completed,
                lesson_date=datetime(2025, 9, 1, 10, 0, 0),
                is_recurring=False,
            )
        )
        await session.commit()
        return group.id


async def _seed_group_15_with_nullable_course_fields(db_engine) -> int:
    from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus

    SessionLocal = async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        group = await session.get(Group, 15)
        if group:
            course = await session.get(Course, group.course_id)
            if course:
                course.max_students = None
                course.duration_months = None
                course.lessons_per_week = None
                course.is_active = None
                await session.commit()
            return group.id

        course = Course(
            name="Smoke Nullable Course",
            language="English",
            level=CourseLevel.beginner,
            category=CourseCategory.children,
            price_per_month=1000,
        )
        session.add(course)
        await session.flush()
        course.max_students = None
        course.duration_months = None
        course.lessons_per_week = None
        course.is_active = None

        group = Group(
            id=15,
            name="Smoke Group 15",
            course_id=course.id,
            status=GroupStatus.recruiting,
        )
        session.add(group)
        await session.commit()
        return group.id


# ═══════════════════════════════════════════════════════════════════════════
# Group 1 — Public endpoints (no auth required, expect 200)
# ═══════════════════════════════════════════════════════════════════════════

async def test_public_root(client: AsyncClient):
    """GET / confirms that the server is alive and returns project metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data or "status" in data


async def test_public_root_utf8_content_type(client: AsyncClient):
    """GET / returns JSON with explicit UTF-8 charset in Content-Type."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "charset=utf-8" in response.headers["content-type"].lower()


async def test_public_news(client: AsyncClient):
    """GET /api/v1/news returns a paginated list (200) without authentication."""
    response = await client.get("/api/v1/news")
    assert response.status_code == 200


async def test_public_news_trailing_slash_returns_404(client: AsyncClient):
    """GET /api/v1/news/ must not redirect with 307 when redirect_slashes is disabled."""
    slash_response = await client.get("/api/v1/news/")
    assert slash_response.status_code == 404

    no_slash_response = await client.get("/api/v1/news")
    assert no_slash_response.status_code == 200


async def test_public_news_categories(client: AsyncClient):
    """GET /api/v1/news/categories/ returns category list JSON, not int parsing."""
    response = await client.get("/api/v1/news/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_public_courses(client: AsyncClient):
    """GET /api/v1/courses returns a list of courses (200) without authentication."""
    response = await client.get("/api/v1/courses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_public_jobs(client: AsyncClient):
    """GET /api/v1/jobs returns a list of job openings (200)."""
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200


async def test_public_catalog_endpoints_without_trailing_slash(client: AsyncClient):
    """List endpoints for teachers/branches/programs must work without trailing slash."""
    for path in ("/api/v1/teachers", "/api/v1/branches", "/api/v1/programs"):
        response = await client.get(path)
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ═══════════════════════════════════════════════════════════════════════════
# Group 2 — Auth endpoints
# ═══════════════════════════════════════════════════════════════════════════

async def test_auth_login_valid(client: AsyncClient, student_token):
    """POST /api/v1/auth/login with valid credentials returns 200 and a token.
    The student user created by the student_token fixture is re-used here."""
    payload = {"email": "student@smoke-tests.example.com", "password": "StudentPass123"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_auth_login_trailing_slash_returns_404(client: AsyncClient):
    """POST /api/v1/auth/login/ must not redirect with 307."""
    payload = {"email": "trailing-slash-check@example.com", "password": "NotUsed123!"}
    slash_response = await client.post("/api/v1/auth/login/", json=payload)
    assert slash_response.status_code == 404

    no_slash_response = await client.post("/api/v1/auth/login", json=payload)
    assert no_slash_response.status_code == 401


async def test_auth_login_wrong_password(client: AsyncClient, student_token):
    """POST /api/v1/auth/login with a wrong password must return 401."""
    payload = {"email": "student@smoke-tests.example.com", "password": "WrongPassword!"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


async def test_auth_login_unknown_email(client: AsyncClient):
    """POST /api/v1/auth/login for an unknown email must return 401 or 404."""
    payload = {"email": "nobody@nowhere-unknown.example.com", "password": "AnyPassword"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code in (401, 404)


# ═══════════════════════════════════════════════════════════════════════════
# Group 3 — Protected endpoints without a token (expect 401)
# ═══════════════════════════════════════════════════════════════════════════

async def test_no_token_schedule(client: AsyncClient):
    """GET /api/v1/schedule without a token returns 401 (requires staff auth)."""
    response = await client.get("/api/v1/schedule")
    assert response.status_code == 401


async def test_no_token_attendance_my(client: AsyncClient):
    """GET /api/v1/attendance/my without a token returns 401."""
    response = await client.get("/api/v1/attendance/my")
    assert response.status_code == 401


async def test_no_token_homeworks_my(client: AsyncClient):
    """GET /api/v1/homeworks/my without a token returns 401."""
    response = await client.get("/api/v1/homeworks/my")
    assert response.status_code == 401


async def test_materials_endpoint_not_404(client: AsyncClient):
    """GET /api/v1/materials?group_id=1 must return 200 or 401, never 404.

    Regression guard: the frontend LessonMaterial.vue page calls
    GET /api/v1/materials?group_id={id} which was previously unregistered,
    causing a 404.  After the fix the route exists and returns 401 when called
    without a token (staff-only endpoint).
    """
    response = await client.get("/api/v1/materials", params={"group_id": 1})
    assert response.status_code in (200, 401), (
        f"GET /api/v1/materials?group_id=1 returned {response.status_code}, "
        "expected 200 or 401 (not 404)"
    )

    response_with_slash = await client.get("/api/v1/materials/", params={"group_id": 1})
    assert response_with_slash.status_code in (200, 401), (
        f"GET /api/v1/materials/?group_id=1 returned {response_with_slash.status_code}, "
        "expected 200 or 401 (not 404)"
    )


async def test_staff_progress_endpoint_not_404(client: AsyncClient, db_engine, teacher_token):
    """GET /api/v1/progress returns the progress payload for staff instead of 404."""
    group_id = await _seed_progress_group(db_engine)

    response = await client.get(
        "/api/v1/progress",
        params={"group_id": group_id, "date_from": "2025-09-01", "date_to": "2025-09-30"},
        headers=auth_headers(teacher_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["group"]["id"] == group_id
    assert data["students"][0]["student_name"] == "Smoke Progress Student"


async def test_progress_dates_post_endpoint_not_404(client: AsyncClient):
    """POST /api/v1/progress/dates returns 200 or 401 (route exists, never 404)."""
    response = await client.post(
        "/api/v1/progress/dates",
        json={"group_id": 1, "lesson_date": "2025-09-01"},
    )
    assert response.status_code in (200, 401), (
        f"POST /api/v1/progress/dates returned {response.status_code}, "
        "expected 200 or 401 (not 404)"
    )


async def test_staff_attendance_group_grades_with_date_range(client: AsyncClient, db_engine, teacher_token):
    """GET /api/v1/attendance/group/{group_id}/grades returns 200 for staff with date filters."""
    group_id = await _seed_progress_group(db_engine)

    response = await client.get(
        f"/api/v1/attendance/group/{group_id}/grades",
        params={"date_from": "2025-09-01", "date_to": "2025-09-30"},
        headers=auth_headers(teacher_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["group"]["id"] == group_id


async def test_student_progress_endpoint_forbidden(client: AsyncClient, db_engine, student_token):
    """GET /api/v1/progress with a student token returns 403 (staff-only endpoint)."""
    group_id = await _seed_progress_group(db_engine)

    response = await client.get(
        "/api/v1/progress",
        params={"group_id": group_id, "date_from": "2025-09-01", "date_to": "2025-09-30"},
        headers=auth_headers(student_token),
    )

    assert response.status_code == 403


async def test_no_token_messages_inbox(client: AsyncClient):
    """GET /api/v1/messages/inbox without a token returns 401."""
    response = await client.get("/api/v1/messages/inbox")
    assert response.status_code == 401


async def test_no_token_students(client: AsyncClient):
    """GET /api/v1/students/ without a token returns 401 (requires staff auth)."""
    response = await client.get("/api/v1/students/")
    assert response.status_code == 401


async def test_no_token_teachers_expects_401(client: AsyncClient):
    """GET /api/v1/teachers/ without a token returns 200 — the endpoint is public."""
    response = await client.get("/api/v1/teachers/")
    assert response.status_code == 200


async def test_staff_get_group_15_with_nullable_course_fields(client: AsyncClient, db_engine, teacher_token):
    """GET /api/v1/groups/15 returns 200 when related nullable course fields are NULL."""
    group_id = await _seed_group_15_with_nullable_course_fields(db_engine)
    assert group_id == 15

    response = await client.get("/api/v1/groups/15", headers=auth_headers(teacher_token))
    assert response.status_code == 200
    assert response.json()["course"]["max_students"] is None


# ═══════════════════════════════════════════════════════════════════════════
# Group 4 — Protected endpoints with a student token (expect 200)
# ═══════════════════════════════════════════════════════════════════════════

async def test_student_schedule_my(client: AsyncClient, student_token: str):
    """GET /api/v1/schedule/my with a student token returns 200.
    /schedule/my is accessible to any authenticated user (require_student)."""
    response = await client.get(
        "/api/v1/schedule/my", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


async def test_student_schedule_full_expects_403(client: AsyncClient, student_token: str):
    """GET /api/v1/schedule with a student token returns 403 — endpoint is staff-only."""
    response = await client.get(
        "/api/v1/schedule", headers=auth_headers(student_token)
    )
    assert response.status_code == 403


async def test_student_attendance_my(client: AsyncClient, student_token: str):
    """GET /api/v1/attendance/my with a student token returns 200."""
    response = await client.get(
        "/api/v1/attendance/my", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


async def test_student_homeworks_my(client: AsyncClient, student_token: str):
    """GET /api/v1/homeworks/my with a student token returns 200."""
    response = await client.get(
        "/api/v1/homeworks/my", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


async def test_teacher_students_without_trailing_slash(client: AsyncClient, teacher_token: str):
    """GET /api/v1/students must work without trailing slash for staff users."""
    response = await client.get(
        "/api/v1/students", headers=auth_headers(teacher_token)
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_other_staff_lists_without_trailing_slash(
    client: AsyncClient,
    student_token: str,
    teacher_token: str,
    admin_token: str,
):
    """Slashless list endpoints updated in v1 routers must not return 404."""
    checks = [
        ("/api/v1/homeworks", teacher_token),
        ("/api/v1/messages", student_token),
        ("/api/v1/forms", teacher_token),
        ("/api/v1/audit", admin_token),
    ]
    for path, token in checks:
        response = await client.get(path, headers=auth_headers(token))
        assert response.status_code == 200


async def test_student_news(client: AsyncClient, student_token: str):
    """GET /api/v1/news with a student token returns 200 (public endpoint)."""
    response = await client.get(
        "/api/v1/news", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# Group 5 — Student tries to access admin/staff routes (expect 403)
# ═══════════════════════════════════════════════════════════════════════════

async def test_student_cannot_access_students_list(client: AsyncClient, student_token: str):
    """GET /api/v1/students/ with a student token returns 403.
    This endpoint requires staff (teacher or admin) access."""
    response = await client.get(
        "/api/v1/students/", headers=auth_headers(student_token)
    )
    assert response.status_code == 403


async def test_student_cannot_access_teachers_list(client: AsyncClient, student_token: str):
    """GET /api/v1/teachers/ with a student token returns 200 — the endpoint is public."""
    response = await client.get(
        "/api/v1/teachers/", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


async def test_student_cannot_access_applications(client: AsyncClient, student_token: str):
    """GET /api/v1/applications with a student token should return 403.
    The endpoint does not exist yet; enrollments are at /api/v1/enrollments/."""
    response = await client.get(
        "/api/v1/applications", headers=auth_headers(student_token)
    )
    assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# Group 6 — CORS preflight (OPTIONS) for the Vercel frontend origin
# ═══════════════════════════════════════════════════════════════════════════

async def test_cors_preflight_vercel_origin(client: AsyncClient):
    """OPTIONS /api/v1/auth/login from the Vercel frontend must return 200.

    This guards against the 400 Bad Request regression caused by the Vercel
    origin missing from allow_origins when allow_credentials=True is set.
    ALLOWED_ORIGINS (or the legacy FRONTEND_URL) must be set to include
    https://abc-school-frontend.vercel.app in production.
    The conftest sets ALLOWED_ORIGINS before the app is imported so the
    CORSMiddleware is initialized with the production-like origin list.
    """
    vercel_origin = "https://abc-school-frontend.vercel.app"

    from app.core.cors import get_cors_origins
    assert vercel_origin in get_cors_origins(), (
        "Vercel frontend origin must appear in get_cors_origins() when "
        "ALLOWED_ORIGINS is set.  Check cors.py."
    )

    response = await client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": vercel_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    # FastAPI CORSMiddleware returns 200 for valid preflight, not 400/403
    assert response.status_code == 200, (
        f"OPTIONS preflight from {vercel_origin} returned "
        f"{response.status_code}, expected 200."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Group 7 — news_status_history insert regression
# Regression guard for: IntegrityError null value in column "id" of relation
# "news_status_history" violates not-null constraint
# ═══════════════════════════════════════════════════════════════════════════

async def test_admin_create_news_inserts_status_history(
    client: AsyncClient, admin_token: str
):
    """POST /api/v1/admin/news must succeed and must insert a NewsStatusHistory
    row with an auto-generated id (not NULL).

    This is a regression test for the production IntegrityError:
      "null value in column 'id' of relation 'news_status_history'
       violates not-null constraint"
    which occurred because the id column lacked a proper sequence default.
    """
    response = await client.post(
        "/api/v1/admin/news",
        headers=auth_headers(admin_token),
        json={
            "title": "Regression: status history id test",
            "body": "Body text for regression test.",
            "status": "draft",
        },
    )
    assert response.status_code == 201, (
        f"Admin news creation failed ({response.status_code}): {response.text}"
    )
    data = response.json()
    assert data.get("id") is not None, "Created news must have a non-null id"
    assert data.get("slug") == f"regression-status-history-id-test-{data['id']}"
    # status_history is returned in the NewsOut schema; verify at least one entry
    assert len(data.get("status_history", [])) >= 1, (
        "NewsStatusHistory insert failed — status_history must contain the "
        "initial status transition record.  Check that the id sequence is "
        "properly set up on the news_status_history table."
    )
    assert data["status_history"][0]["id"] is not None, (
        "NewsStatusHistory.id is None — the auto-increment sequence is broken."
    )


async def test_publish_scheduled_news_inserts_status_history(
    client: AsyncClient, admin_token: str
):
    """Scheduled publish must append a status-history row with non-null id."""
    title = f"Regression scheduled publish {uuid4()}"
    create_response = await client.post(
        "/api/v1/admin/news",
        headers=auth_headers(admin_token),
        json={
            "title": title,
            "body": "Body text for scheduler regression test.",
            "status": "scheduled",
            "publish_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert create_response.status_code == 201, (
        f"Scheduled news creation failed ({create_response.status_code}): "
        f"{create_response.text}"
    )
    created_news = create_response.json()
    news_id = created_news["id"]

    publish_response = await client.post("/api/v1/admin/news/publish-scheduled")
    assert publish_response.status_code == 200, (
        f"Scheduled publish failed ({publish_response.status_code}): "
        f"{publish_response.text}"
    )
    publish_data = publish_response.json()
    assert title in publish_data.get("titles", []), (
        "Expected scheduled news title in scheduler response, but it was missing."
    )

    details_response = await client.get(f"/api/v1/news/{news_id}")
    assert details_response.status_code == 200, (
        f"Fetching published news failed ({details_response.status_code}): "
        f"{details_response.text}"
    )
    details = details_response.json()
    auto_publish_history = [
        row for row in details.get("status_history", [])
        if row.get("from_status") == "scheduled" and row.get("to_status") == "published"
    ]
    assert auto_publish_history, (
        "Missing scheduled -> published history row after scheduler publish."
    )
    assert auto_publish_history[-1].get("id") is not None, (
        "Scheduled publish history row has null id; sequence/default is broken."
    )


# ═══════════════════════════════════════════════════════════════════════════
# Group 8 — Forms smoke regressions
# ═══════════════════════════════════════════════════════════════════════════

async def test_post_adult_form_returns_success(client: AsyncClient):
    """POST /api/v1/forms/adult with minimal valid payload returns success."""
    payload = {
        "fio": "Петров Иван Иванович",
        "phone": "+79001234567",
        "address": "ул. Пушкина, 10",
    }
    response = await client.post("/api/v1/forms/adult", json=payload)
    assert response.status_code == 200, (
        f"POST /api/v1/forms/adult failed ({response.status_code}): {response.text}"
    )
    body = response.json()
    assert body.get("id") is not None


# ═══════════════════════════════════════════════════════════════════════════
# Group 8 — Teacher form snake_case field names (regression guard for 422)
# ═══════════════════════════════════════════════════════════════════════════

async def test_post_teacher_form_snake_case_fields_not_422(client: AsyncClient):
    """POST /api/v1/forms/teacher with snake_case field names must not return 422.

    The frontend sends birth_info, marital_status, work_experience and
    language_level in snake_case.  The Pydantic schema must accept both
    snake_case (populate_by_name=True) and camelCase (via Field alias) so
    that the endpoint returns 200/201, not a 422 validation error.
    """
    payload = {
        "fio": "Иванова Мария Петровна",
        "birth_info": "01.01.1990, г. Москва",
        "marital_status": "замужем",
        "education": "Высшее",
        "work_experience": "5 лет",
        "language_level": "B2",
        "skills": "Python, FastAPI",
        "qualities": "Ответственность",
        "address": "ул. Ленина, 1",
        "phone": "+79001234567",
        "email": "teacher@example.com",
    }
    response = await client.post("/api/v1/forms/teacher", json=payload)
    assert response.status_code != 422, (
        f"POST /api/v1/forms/teacher with snake_case fields returned 422. "
        f"Response: {response.text}"
    )
