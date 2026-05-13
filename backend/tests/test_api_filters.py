"""API-фильтры: проверка канонических списков через ASGI-клиент.

Тесты проверяют, что:
  - GET /api/v1/branches?for_schedule=true возвращает 21 учебный филиал
  - GET /api/v1/teachers возвращает ровно 27 записей (20 английского + 7 китайского)
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
        classroom = Classroom(
            name="Кабинет 1",
            capacity=12,
            branch_id=teaching_branches[0].id,
            is_active=True,
        )
        session.add(classroom)
        await session.flush()

        # ── Группа с преподавателем в учебном филиале ────────────────────────
        group = Group(
            name="Тест-группа A1",
            course_id=last_course.id,
            teacher_id=teacher_objs[0].id,
            status=GroupStatus.active,
            language="Китайский",
            program_name="Китайский язык",
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

        lesson_with_null_branch = Lesson(
            group_id=group.id,
            teacher_id=teacher_objs[0].id,
            classroom_id=classroom.id,
            branch_id=None,
            program_id=program_objs[0].id,
            day_of_week=DayOfWeek.thursday,
            time_start=time(11, 0),
            time_end=time(12, 0),
            topic="NULL_BRANCH",
            status=LessonStatus.scheduled,
            is_recurring=True,
        )
        session.add(lesson_with_null_branch)

        # ── Завершённая группа — не должна попадать в /groups по умолчанию ──
        finished_group = Group(
            name="Тест-группа OLD-2024",
            course_id=last_course.id,
            teacher_id=teacher_objs[0].id,
            status=GroupStatus.finished,
        )
        session.add(finished_group)
        await session.flush()

        finished_lesson = Lesson(
            group_id=finished_group.id,
            teacher_id=teacher_objs[0].id,
            classroom_id=classroom.id,
            branch_id=teaching_branches[0].id,
            program_id=program_objs[0].id,
            day_of_week=DayOfWeek.tuesday,
            time_start=time(10, 0),
            time_end=time(11, 0),
            status=LessonStatus.scheduled,
            is_recurring=False,
        )
        session.add(finished_lesson)

        # ── Приостановленная группа — тоже не должна попадать по умолчанию ──
        suspended_group = Group(
            name="Тест-группа SUSPENDED",
            course_id=last_course.id,
            teacher_id=teacher_objs[1].id,
            status=GroupStatus.suspended,
        )
        session.add(suspended_group)
        await session.flush()

        suspended_lesson = Lesson(
            group_id=suspended_group.id,
            teacher_id=teacher_objs[1].id,
            classroom_id=classroom.id,
            branch_id=teaching_branches[1].id,
            program_id=program_objs[0].id,
            day_of_week=DayOfWeek.wednesday,
            time_start=time(12, 0),
            time_end=time(13, 0),
            status=LessonStatus.scheduled,
            is_recurring=False,
        )
        session.add(suspended_lesson)

        # ── Группа без занятий — не должна попадать в /groups по умолчанию ─
        orphan_group = Group(
            name="Тест-группа БЕЗ-УРОКОВ",
            course_id=last_course.id,
            teacher_id=teacher_objs[0].id,
            status=GroupStatus.recruiting,
        )
        session.add(orphan_group)

        await session.commit()

    return filter_db_engine


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def filter_client(seeded_filter_db):
    """AsyncClient с ASGI-транспортом, переопределённой get_db и JWT-токеном admin."""
    from app.core.database import get_db
    from app.core.security import hash_password, create_access_token
    from app.main import app
    from app.models.user import User, UserRole

    SessionLocal = async_sessionmaker(
        bind=seeded_filter_db, class_=AsyncSession, expire_on_commit=False
    )

    # Создаём тестового admin-пользователя в тестовой БД
    async with SessionLocal() as session:
        admin = User(
            email="filter-test-admin@test.local",
            hashed_password=hash_password("TestPass123"),
            full_name="Тест Фильтр Админ",
            role=UserRole.admin,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        token = create_access_token(
            {"sub": str(admin.id), "email": admin.email, "role": admin.role.value}
        )

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
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


async def test_classrooms_api_includes_branch_name(filter_client: AsyncClient):
    """GET /api/v1/classrooms возвращает branch_id и branch_name для аудитории."""
    classrooms_response = await filter_client.get("/api/v1/classrooms")
    assert classrooms_response.status_code == 200
    classrooms = classrooms_response.json()
    classroom = next((item for item in classrooms if item["name"] == "Кабинет 1"), None)
    assert classroom is not None
    assert classroom["branch_id"] is not None
    branches_response = await filter_client.get("/api/v1/branches")
    assert branches_response.status_code == 200
    branch_map = {branch["id"]: branch["name"] for branch in branches_response.json()}
    assert classroom["branch_name"] == branch_map[classroom["branch_id"]]


async def test_schedule_uses_classroom_branch_when_lesson_branch_is_null(filter_client: AsyncClient):
    """GET /api/v1/schedule должен получать филиал из classrooms.branch_id."""
    schedule_response = await filter_client.get("/api/v1/schedule")
    assert schedule_response.status_code == 200
    schedule_data = schedule_response.json()
    lesson = next((item for item in schedule_data if item.get("topic") == "NULL_BRANCH"), None)
    assert lesson is not None
    assert lesson["branch_id"] is not None
    classrooms_response = await filter_client.get("/api/v1/classrooms")
    assert classrooms_response.status_code == 200
    classroom = next(
        (item for item in classrooms_response.json() if item["id"] == lesson["classroom_id"]),
        None,
    )
    assert classroom is not None
    assert lesson["branch_name"] == classroom["branch_name"]


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
    """GET /api/v1/teachers — 20 преподавателей английского и 7 китайского."""
    response = await filter_client.get("/api/v1/teachers")
    assert response.status_code == 200
    data = response.json()
    english = [t for t in data if t.get("subject") == "Английский"]
    chinese = [t for t in data if t.get("subject") == "Китайский"]
    assert len(english) == 20, f"Ожидалось 20 преподавателей английского, получено {len(english)}"
    assert len(chinese) == 7, f"Ожидалось 7 преподавателей китайского, получено {len(chinese)}"


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


async def test_groups_api_default_returns_only_active_and_recruiting(filter_client: AsyncClient):
    """GET /api/v1/groups по умолчанию возвращает только активные/набирающиеся группы."""
    response = await filter_client.get("/api/v1/groups")
    assert response.status_code == 200
    data = response.json()
    names = [g["name"] for g in data]
    assert "Тест-группа OLD-2024" not in names, (
        "Завершённая группа не должна попадать в /groups по умолчанию"
    )
    assert "Тест-группа SUSPENDED" not in names, (
        "Приостановленная группа не должна попадать в /groups по умолчанию"
    )
    assert "Тест-группа БЕЗ-УРОКОВ" not in names, (
        "Группа без занятий не должна попадать в /groups по умолчанию"
    )


async def test_groups_api_default_includes_active_group(filter_client: AsyncClient):
    """GET /api/v1/groups возвращает активную группу с учебным расписанием."""
    response = await filter_client.get("/api/v1/groups")
    assert response.status_code == 200
    data = response.json()
    names = [g["name"] for g in data]
    assert "Тест-группа A1" in names, (
        "Активная группа с учебным расписанием должна возвращаться в /groups"
    )
    for g in data:
        assert g["status"] in ("active", "recruiting"), (
            f"Группа '{g['name']}' имеет статус '{g['status']}', ожидалось active или recruiting"
        )


async def test_groups_api_includes_course_language_and_program_name(filter_client: AsyncClient):
    """GET /api/v1/groups возвращает language и program_name прямо из таблицы groups."""
    groups_response = await filter_client.get("/api/v1/groups")
    assert groups_response.status_code == 200
    groups = groups_response.json()
    assert groups

    for group in groups:
        assert "language" in group
        assert "program_name" in group

    # Проверяем что "Тест-группа A1" имеет правильные прямые значения
    a1 = next((g for g in groups if g["name"] == "Тест-группа A1"), None)
    assert a1 is not None
    assert a1["language"] == "Китайский"
    assert a1["program_name"] == "Китайский язык"


async def test_groups_api_active_only_false_includes_all_statuses(filter_client: AsyncClient):
    """GET /api/v1/groups?active_only=false возвращает все группы, включая завершённые."""
    response = await filter_client.get("/api/v1/groups", params={"active_only": "false"})
    assert response.status_code == 200
    data = response.json()
    names = [g["name"] for g in data]
    assert "Тест-группа OLD-2024" in names, (
        "При active_only=false завершённая группа должна присутствовать"
    )
    assert "Тест-группа SUSPENDED" in names, (
        "При active_only=false приостановленная группа должна присутствовать"
    )
    assert "Тест-группа A1" in names, (
        "При active_only=false активная группа тоже должна присутствовать"
    )


async def test_groups_api_active_only_false_includes_orphan(filter_client: AsyncClient):
    """GET /api/v1/groups?active_only=false возвращает группы без занятий (статус recruiting)."""
    response = await filter_client.get("/api/v1/groups", params={"active_only": "false"})
    assert response.status_code == 200
    data = response.json()
    names = [g["name"] for g in data]
    assert "Тест-группа БЕЗ-УРОКОВ" in names, (
        "При active_only=false группа без занятий (recruiting) должна присутствовать"
    )
