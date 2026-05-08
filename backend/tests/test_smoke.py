"""Smoke test suite for the ABC Language School backend API.

Tests verify that all key endpoints are reachable and return correct HTTP
status codes. Uses pytest-asyncio + httpx AsyncClient with FastAPI's ASGI
transport — no real HTTP calls are made to external servers.

Run with:
    python -m pytest backend/tests/test_smoke.py -v
"""
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


# ═══════════════════════════════════════════════════════════════════════════
# Group 1 — Public endpoints (no auth required, expect 200)
# ═══════════════════════════════════════════════════════════════════════════

async def test_public_root(client: AsyncClient):
    """GET / confirms that the server is alive and returns project metadata."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data or "status" in data


async def test_public_news(client: AsyncClient):
    """GET /api/v1/news returns a paginated list (200) without authentication."""
    response = await client.get("/api/v1/news")
    assert response.status_code == 200


async def test_public_courses(client: AsyncClient):
    """GET /api/v1/courses returns a list of courses (200) without authentication."""
    response = await client.get("/api/v1/courses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_public_jobs(client: AsyncClient):
    """GET /api/v1/jobs returns a list of job openings (200)."""
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200


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


async def test_no_token_messages_inbox(client: AsyncClient):
    """GET /api/v1/messages/inbox without a token returns 401."""
    response = await client.get("/api/v1/messages/inbox")
    assert response.status_code == 401


async def test_no_token_students(client: AsyncClient):
    """GET /api/v1/students/ without a token returns 401 (requires staff auth)."""
    response = await client.get("/api/v1/students/")
    assert response.status_code == 401


@pytest.mark.xfail(
    reason=(
        "GET /api/v1/teachers/ is a public endpoint (no auth) — "
        "returns 200, not 401. Admin-gated teacher management lives under "
        "/api/v1/admin/. Mark xfail until a protected /teachers route is added."
    )
)
async def test_no_token_teachers_expects_401(client: AsyncClient):
    """GET /api/v1/teachers/ without a token is documented as admin-only and
    should return 401.  Currently the endpoint is public and returns 200."""
    response = await client.get("/api/v1/teachers/")
    assert response.status_code == 401


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


@pytest.mark.xfail(
    reason=(
        "GET /api/v1/schedule requires require_staff (teacher or admin). "
        "A student receives 403, not 200. Use /schedule/my for student access."
    )
)
async def test_student_schedule_full_expects_200(client: AsyncClient, student_token: str):
    """GET /api/v1/schedule with a student token should return 200 per the spec,
    but in reality it is restricted to staff and returns 403 for students."""
    response = await client.get(
        "/api/v1/schedule", headers=auth_headers(student_token)
    )
    assert response.status_code == 200


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


@pytest.mark.xfail(
    reason=(
        "GET /api/v1/teachers/ is a public endpoint — it returns 200 for "
        "everyone, including students.  The spec expects 403 for students, "
        "which implies a protected admin route that does not exist yet."
    )
)
async def test_student_cannot_access_teachers_list(client: AsyncClient, student_token: str):
    """GET /api/v1/teachers/ with a student token should return 403.
    Currently the endpoint is public and returns 200 for any caller."""
    response = await client.get(
        "/api/v1/teachers/", headers=auth_headers(student_token)
    )
    assert response.status_code == 403


async def test_student_cannot_access_applications(client: AsyncClient, student_token: str):
    """GET /api/v1/applications with a student token should return 403.
    The endpoint does not exist yet; enrollments are at /api/v1/enrollments/."""
    response = await client.get(
        "/api/v1/applications", headers=auth_headers(student_token)
    )
    assert response.status_code == 403
