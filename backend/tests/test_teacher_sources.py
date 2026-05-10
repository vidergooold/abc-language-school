import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CANONICAL_TEACHERS = {
    "Арнгольд Валерия Евгеньевна",
    "Белова Александра Анатольевна",
    "Быковская Марина Эдуардовна",
    "Винокурова Елена Александровна",
    "Воронцова Анна Вадимовна",
    "Данилова Мария Анатольевна",
    "Евдокимова Полина Евгеньевна",
    "Зудяева Надежда Андреевна",
    "Иванова Мария Петровна",
    "Караваева Алина Денисовна",
    "Козлова Елена Геннадьевна",
    "Колесник Любовь Николаевна",
    "Куцых Марина Евгеньевна",
    "Лукьянова Светлана Ярославовна",
    "Митина Ольга Сергеевна",
    "Осинина Светлана Николаевна",
    "Пасикан Ангелина Сергеевна",
    "Переведенцева Александра Андреевна",
    "Позднякова Виктория Сергеевна",
    "Походная Алёна Игоревна",
    "Родина Татьяна Петровна",
    "Рубе Дарья Васильевна",
    "Темлякова Анна Михайловна",
    "Тихвинская Виктория Олеговна",
    "Турабова Диана Джейхуновна",
    "Федорова Анфиса Вячеславовна",
    "Фомина Снежанна Олеговна",
}


def _parse_seed_teacher_names() -> set[str]:
    source = (ROOT / "backend/seed_teachers.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "TEACHERS_DATA"
                for target in node.targets
            )
        ):
            entries = ast.literal_eval(node.value)
            return {entry["full_name"] for entry in entries}
    raise AssertionError("TEACHERS_DATA constant not found in seed_teachers.py")


def _parse_migration_teacher_names() -> set[str]:
    source = (
        ROOT / "backend/alembic/versions/e1f2a3b4c5d6_normalize_canonical_branch_teacher_classroom_data.py"
    ).read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "_ALLOWED_TEACHER_NAMES"
                for target in node.targets
            )
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError("_ALLOWED_TEACHER_NAMES constant not found in migration")


def test_seed_teachers_only_canonical():
    assert _parse_seed_teacher_names() == CANONICAL_TEACHERS


def test_migration_allows_only_canonical_teachers():
    assert _parse_migration_teacher_names() == CANONICAL_TEACHERS


def test_obsolete_teachers_not_in_seed_sources():
    obsolete = {
        "Григорьева Дарья Дмитриевна",
        "Кривилева Галина Александровна",
        "Стафеева Яна Викторовна",
        "Демо Преподаватель",
    }
    source_bundle = "\n".join(
        [
            (ROOT / "backend/seed_account_data.py").read_text(encoding="utf-8"),
            (ROOT / "backend/seed_demo.py").read_text(encoding="utf-8"),
            (ROOT / "frontend/src/pages/organization/Staff.vue").read_text(encoding="utf-8"),
        ]
    )
    for name in obsolete:
        assert name not in source_bundle, f"Obsolete teacher '{name}' found in sources"
