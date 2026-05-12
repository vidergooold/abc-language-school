import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from seed_distribution import PROGRAM_TO_GROUP_NAME
from seed_real_schedule import GROUPS_SCHEDULE


CANONICAL_GROUP_NAMES = {
    "Дошкольники",
    "FH1",
    "AS1",
    "AS2",
    "AS3",
    "AS4",
    "GWA1+",
    "GWA2",
    "GWB1",
    "GWB1+",
    "GWB2",
    "GWB2+",
    "GWC1",
    "Взрослые групповые",
    "Мини-группа (2 чел.)",
    "Индивидуальные занятия",
    "Китайский",
    "Английский FH1",
    "Английский AS2",
    "Английский AS1",
    "Китайский HSK1",
}

SEED_FILES = [
    ROOT / "backend/seed_real_schedule.py",
    ROOT / "backend/seed_distribution.py",
    ROOT / "backend/seed_demo.py",
    ROOT / "backend/seed_account_data.py",
    ROOT / "backend/seeds/seed_all.py",
]


def _collect_group_names_from_get_or_create_calls(path: Path) -> set[str]:
    names: set[str] = set()
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source)

    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue

        if not any(isinstance(arg, ast.Name) and arg.id == "Group" for arg in node.args):
            continue

        for keyword in node.keywords:
            if keyword.arg == "name" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                names.add(keyword.value.value)

        for arg in node.args:
            if not isinstance(arg, ast.Dict):
                continue
            for key_node, value_node in zip(arg.keys, arg.values):
                if (
                    isinstance(key_node, ast.Constant)
                    and key_node.value == "name"
                    and isinstance(value_node, ast.Constant)
                    and isinstance(value_node.value, str)
                ):
                    names.add(value_node.value)

    return names


def test_group_names_in_seed_sources_are_canonical():
    schedule_group_names = {entry["group_name"] for entry in GROUPS_SCHEDULE}
    generated_group_names = set(PROGRAM_TO_GROUP_NAME.values())
    static_seed_group_names = (
        _collect_group_names_from_get_or_create_calls(ROOT / "backend/seed_demo.py")
        | _collect_group_names_from_get_or_create_calls(ROOT / "backend/seed_account_data.py")
    )

    all_group_names = schedule_group_names | generated_group_names | static_seed_group_names
    assert all_group_names <= CANONICAL_GROUP_NAMES


def test_no_german_or_french_in_seed_sources():
    forbidden_tokens = ("Немецкий", "Французский")
    for path in SEED_FILES:
        content = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in content


def test_seed_account_groups_use_language_program_format():
    names = _collect_group_names_from_get_or_create_calls(ROOT / "backend/seed_account_data.py")
    assert {
        "Английский FH1",
        "Английский AS2",
        "Английский AS1",
        "Китайский HSK1",
    } <= names
    assert "FH1" not in names
    assert "Взрослые групповые" not in names
