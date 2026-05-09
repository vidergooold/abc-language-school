import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CANONICAL_TEACHERS = {
    "Белова Александра Анатольевна",
    "Григорьева Дарья Дмитриевна",
    "Данилова Мария Анатольевна",
    "Евдокимова Полина Евгеньевна",
    "Колесник Любовь Николаевна",
    "Куцых Марина Евгеньевна",
    "Кривилева Галина Александровна",
    "Лукьянова Светлана Ярославовна",
    "Митина Ольга Сергеевна",
    "Осинина Светлана Николаевна",
    "Пасикан Ангелина Сергеевна",
    "Переведенцева Александра Андреевна",
    "Позднякова Виктория Сергеевна",
    "Рубе Дарья Васильевна",
    "Стафеева Яна Викторовна",
    "Темлякова Анна Михайловна",
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
        ROOT / "backend/alembic/versions/b1c2d3e4f5a6_cleanup_obsolete_teachers.py"
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


def test_obsolete_teachers_not_in_seed_account_data():
    obsolete = {
        "Иванова Анна Сергеевна",
        "Петров Михаил Андреевич",
        "Сидорова Елена Викторовна",
        "Кузнецов Дмитрий Олегович",
        "Морозова Ольга Ивановна",
    }
    seed_account = (ROOT / "backend/seed_account_data.py").read_text(encoding="utf-8")
    for name in obsolete:
        assert name not in seed_account, f"Obsolete teacher '{name}' found in seed_account_data.py"
