"""API-фильтры: проверка канонических списков через ASGI-клиент.

Тесты проверяют, что:
  - GET /api/v1/branches?for_schedule=true возвращает 21 учебный филиал
  - GET /api/v1/teachers возвращает ровно 27 записей (24 английского + 3 китайского)
  - GET /api/v1/programs возвращает ровно 9 записей
  - GET /api/v1/groups — у каждой группы есть teacher_id
  - административные филиалы не встречаются как branch_id в занятиях

Запуск:
    DATABASE_URL=sqlite+aiosqlite:///:memory: SECRET_KEY=test-secret \
        python -m pytest backend/tests/test_api_filters.py -v
"""
import sys
from datetime import time
from pathlib import Path

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

CANONICAL_TEACHER_COUNT = 27
CANONICAL_PROGRAM_COUNT = 9
CANONICAL_BRANCH_COUNT = 21
CANONICAL_TEACHING_BRANCH_COUNT = 21


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def filter_db_engine():
    """In-memory SQLite engine с полной схемой для тестов фильтров."""
    from app.core.database import Base
    import app.main  # noqa: F401 — регистрирует все модели

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def seeded_filter_db(filter_db_engine):
    """Загружает канонические данные (филиалы, преподаватели, программы, группы) в тестовую БД."""
    from app.models.branch import Branch
    from app.models.educational_program import EducationalProgram
    from app.models.group import Course, Group, GroupStatus
    from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
    from app.models.teacher import Teacher

    from seed_branches_22 import BRANCHES
    from seed_teachers import TEACHERS_DATA
    from seeds.seed_all import COURSES_DATA

    SessionLocal = async_sessionmaker(
        bind=filter_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        # ── Филиалы ─────────────────────────────────────────────────────────
        branch_objs = []
        for row in BRANCHES:
            branch = Branch(
                name=row["name"],
                address=row["address"],
                phone=row.get("phone"),
                email=row.get("email"),
                manager_name=row.get("manager_name"),
                manager_position=row.get("manager_position"),
                working_hours=row.get("working_hours"),
                is_active=True,
                is_administrative=row.get("is_administrative", False),
            )
            session.add(branch)
            branch_objs.append(branch)
        await session.flush()

        teaching_branches = [b for b in branch_objs if not b.is_administrative]

        # ── Преподаватели ────────────────────────────────────────────────────
        teacher_objs = []
        for td in TEACHERS_DATA:
            t = Teacher(**td)
            session.add(t)
            teacher_objs.append(t)
        await session.flush()

        # ── Программы и курсы ───────────────────────────────────────────────
        program_objs = []
        last_course = None
        for cd in COURSES_DATA:
            course = Course(
                name=cd["name"],
                language=cd["language"],
                level=cd["level"],
                category=cd["category"],
                price_per_month=cd["price_per_month"],
                lessons_per_week=cd["lessons_per_week"],
                duration_months=9,
                max_students=12,
                is_active=True,
            )
            session.add(course)
            last_course = course
            prog = EducationalProgram(
                name=cd["name"],
                code=cd["name"],
                language=cd["language"],
                level=None,
                target_group="тест",
                duration_months=9,
                description="Тестовая программа",
                is_active=True,
            )
            session.add(prog)
            program_objs.append(prog)
        await session.flush()

        # ── Кабинет ─────────────────────────────────────────────────────────
        classroom = Classroom(name="Кабинет 1", capacity=12, is_active=True)
        session.add(classroom)
        await session.flush()

        # ── Группа с преподавателем в учебном филиале ────────────────────────
        group = Group(
            name="Тест-группа A1",
            course_id=last_course.id,
            teacher_id=teacher_objs[0].id,
            status=GroupStatus.active,
        )
        session.add(group)
        await session.flush()

        # Занятие в учебном (не административном) филиале
        lesson = Lesson(
            group_id=group.id,
            teacher_id=teacher_objs[0].id,
            classroom_id=classroom.id,
            branch_id=teaching_branches[0].id,
            program_id=program_objs[0].id,
            day_of_week=DayOfWeek.monday,
            time_start=time(10, 0),
            time_end=time(11, 0),
            status=LessonStatus.scheduled,
            is_recurring=True,
        )
        session.add(lesson)
        await session.commit()

    return filter_db_engine


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def filter_client(seeded_filter_db):
    """AsyncClient с ASGI-транспортом и переопределённой зависимостью get_db."""
    from app.core.database import get_db
    from app.main import app

    SessionLocal = async_sessionmaker(
        bind=seeded_filter_db, class_=AsyncSession, expire_on_commit=False
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


# ── Тесты ────────────────────────────────────────────────────────────────────


async def test_branches_full_list_includes_only_canonical(filter_client: AsyncClient):
    """GET /api/v1/branches без фильтров возвращает все 21 активный канонический филиал."""
    response = await filter_client.get("/api/v1/branches")
    assert response.status_code == 200
    data = response.json()
    names = [b["name"] for b in data]
    assert "Офис" not in names, "Офис исключён, так как не входит в утверждённый список из 21 филиала"
    assert len(data) == CANONICAL_BRANCH_COUNT, (
        f"Ожидалось {CANONICAL_BRANCH_COUNT} филиалов, получено {len(data)}"
    )


async def test_branches_have_no_administrative_entries(filter_client: AsyncClient):
    """GET /api/v1/branches — в каноническом наборе нет административных филиалов."""
    response = await filter_client.get("/api/v1/branches")
    assert response.status_code == 200
    data = response.json()
    assert all(not branch["is_administrative"] for branch in data)


async def test_branches_for_schedule_excludes_office(filter_client: AsyncClient):
    """GET /api/v1/branches?for_schedule=true возвращает те же 21 учебный филиал."""
    response = await filter_client.get("/api/v1/branches", params={"for_schedule": "true"})
    assert response.status_code == 200
    data = response.json()
    names = [b["name"] for b in data]
    assert "Офис" not in names
    assert len(data) == CANONICAL_TEACHING_BRANCH_COUNT, (
        f"Ожидалось {CANONICAL_TEACHING_BRANCH_COUNT} учебных филиалов, получено {len(data)}"
    )


async def test_teachers_returns_canonical_count(filter_client: AsyncClient):
    """GET /api/v1/teachers возвращает ровно 18 активных преподавателей."""
    response = await filter_client.get("/api/v1/teachers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == CANONICAL_TEACHER_COUNT, (
        f"Ожидалось {CANONICAL_TEACHER_COUNT} преподавателей, получено {len(data)}"
    )


async def test_teachers_all_have_subject(filter_client: AsyncClient):
    """GET /api/v1/teachers — у каждого преподавателя указан предмет (English/Chinese)."""
    response = await filter_client.get("/api/v1/teachers")
    assert response.status_code == 200
    data = response.json()
    for teacher in data:
        assert teacher.get("subject"), (
            f"У преподавателя {teacher.get('full_name', '?')} не указан предмет"
        )


async def test_teachers_english_and_chinese_split(filter_client: AsyncClient):
    """GET /api/v1/teachers — 24 преподавателя английского и 3 китайского."""
    response = await filter_client.get("/api/v1/teachers")
    assert response.status_code == 200
    data = response.json()
    english = [t for t in data if t.get("subject") == "Английский"]
    chinese = [t for t in data if t.get("subject") == "Китайский"]
    assert len(english) == 24, f"Ожидалось 24 преподавателя английского, получено {len(english)}"
    assert len(chinese) == 3, f"Ожидалось 3 преподавателя китайского, получено {len(chinese)}"


async def test_programs_returns_canonical_count(filter_client: AsyncClient):
    """GET /api/v1/programs возвращает ровно 9 активных программ."""
    response = await filter_client.get("/api/v1/programs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == CANONICAL_PROGRAM_COUNT, (
        f"Ожидалось {CANONICAL_PROGRAM_COUNT} программ, получено {len(data)}"
    )


async def test_groups_all_have_teacher_id(seeded_filter_db):
    """В БД у каждой группы есть teacher_id (не None)."""
    from sqlalchemy import select
    from app.models.group import Group

    SessionLocal = async_sessionmaker(
        bind=seeded_filter_db, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()

    assert groups, "В БД должна быть хотя бы одна группа"
    for group in groups:
        assert group.teacher_id is not None, (
            f"Группа '{group.name}' (id={group.id}) не имеет teacher_id"
        )


async def test_administrative_branches_not_used_as_lesson_branch(seeded_filter_db):
    """Административные филиалы (если есть) не должны использоваться в lessons."""
    from sqlalchemy import select
    from app.models.branch import Branch
    from app.models.schedule import Lesson

    SessionLocal = async_sessionmaker(
        bind=seeded_filter_db, class_=AsyncSession, expire_on_commit=False
    )
    async with SessionLocal() as session:
        admin_result = await session.execute(
            select(Branch.id).where(Branch.is_administrative == True)
        )
        admin_ids = [row[0] for row in admin_result.all()]
        if not admin_ids:
            return
        lessons_result = await session.execute(
            select(Lesson).where(Lesson.branch_id.in_(admin_ids))
        )
        admin_lessons = lessons_result.scalars().all()

    assert len(admin_lessons) == 0
