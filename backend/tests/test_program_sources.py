import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CANONICAL_PROGRAM_PRICES = {
    "Дошкольники": 2700,
    "FH1, AS1": 3100,
    "AS2, AS3, AS4": 3500,
    "GWA1+, GWA2": 4250,
    "GWB1, GWB1+, GWB2, GWB2+, GWC1": 4900,
    "Взрослые групповые": 6500,
    "Мини-группа (2 чел.)": 6600,
    "Индивидуальные занятия": 1100,
    "Китайский язык": 1200,
}


def _parse_seed_course_prices() -> dict[str, int]:
    source = (ROOT / "backend/seeds/seed_all.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "COURSES_DATA"
            for target in node.targets
        ):
            prices: dict[str, int] = {}
            for entry in node.value.elts:
                if not isinstance(entry, ast.Dict):
                    continue
                name = None
                price = None
                for key_node, value_node in zip(entry.keys, entry.values):
                    if isinstance(key_node, ast.Constant) and key_node.value == "name":
                        if isinstance(value_node, ast.Constant):
                            name = str(value_node.value)
                    if isinstance(key_node, ast.Constant) and key_node.value == "price_per_month":
                        if isinstance(value_node, ast.Constant):
                            price = int(value_node.value)
                if name is not None and price is not None:
                    prices[name] = price
            return prices
    raise AssertionError("COURSES_DATA constant not found in backend/seeds/seed_all.py")


def _parse_migration_course_prices() -> dict[str, int]:
    source = (
        ROOT / "backend/alembic/versions/c7d8e9f0a1b2_cleanup_obsolete_programs_and_sync_prices.py"
    ).read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_CANONICAL_COURSES"
            for target in node.targets
        ):
            entries = ast.literal_eval(node.value)
            return {entry[0]: entry[1] for entry in entries}
    raise AssertionError("_CANONICAL_COURSES constant not found in migration")


def test_seed_courses_match_canonical_program_prices():
    assert _parse_seed_course_prices() == CANONICAL_PROGRAM_PRICES


def test_migration_courses_match_canonical_program_prices():
    assert _parse_migration_course_prices() == CANONICAL_PROGRAM_PRICES


def test_obsolete_program_names_not_present_in_seed_sources():
    obsolete = {
        "Английский — базовый уровень",
        "Немецкий — средний",
        "Французский — продвинутый",
        "Испанский — A1",
        "Подготовка к IELTS",
        "Дошкольный английский 4–6 лет",
        "English Start A1",
        "English Progress A2",
        "Английский для школьников",
        "Разговорный английский для взрослых",
    }
    seed_all = (ROOT / "backend/seeds/seed_all.py").read_text(encoding="utf-8")
    seed_account = (ROOT / "backend/seed_account_data.py").read_text(encoding="utf-8")
    seed_demo = (ROOT / "backend/seed_demo.py").read_text(encoding="utf-8")
    for name in obsolete:
        assert name not in seed_all
        assert name not in seed_account
        assert name not in seed_demo
