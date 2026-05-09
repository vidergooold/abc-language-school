import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_BRANCHES = {
    "Офис",
    "Филиал в МАОУ Гимназия 11 «Гармония»",
    "Филиал в МБОУ СОШ №56",
    "Филиал в МБОУ СОШ №188",
    "Филиал в МАОУ СОШ №218",
    "Филиал в МАОУ «Гимназия №7 «Сибирская»",
    "Филиал в МБОУ СОШ №186",
    "Филиал в МБОУ СОШ №11",
    "Филиал в МБОУ СОШ №2",
    "Филиал в МБОУ СОШ №199",
    "Филиал в МБОУ СОШ №155",
    "Филиал в МАОУ ЛИТ",
    "Филиал в МАОУ НГПЛ",
    "Филиал в МБОУ Гимназия №9",
    "Филиал в МАОУ НЭЛ",
    "Филиал в МАОУ СОШ №216",
    "Филиал в МАОУ СОШ №217",
    "Филиал в МБОУ гимназия №5",
    "Филиал в МБОУ СОШ № 121 «Академическая»",
    "Филиал в МБОУ СОШ № 61 им. Н.М.Иванова",
    "Филиал в МАОУ «СОШ №222»",
}


def _parse_seed_branches() -> set[str]:
    source = (ROOT / "backend/seed_branches_22.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "BRANCHES" for target in node.targets):
            return {entry["name"] for entry in ast.literal_eval(node.value)}
    raise AssertionError("BRANCHES constant not found")


def _parse_sql_branch_names() -> set[str]:
    source = (ROOT / "backend/seeds/branches.sql").read_text(encoding="utf-8")
    return set(re.findall(r"\(\s*'([^']+)'\s*,", source))


def test_seed_sources_only_keep_active_branches():
    assert _parse_seed_branches() == ALLOWED_BRANCHES
    assert _parse_sql_branch_names() == ALLOWED_BRANCHES


def test_other_hardcoded_branch_names_are_normalized():
    seed_account = (ROOT / "backend/seed_account_data.py").read_text(encoding="utf-8")
    seed_demo = (ROOT / "backend/seed_demo.py").read_text(encoding="utf-8")
    general_page = (ROOT / "frontend/src/pages/organization/General.vue").read_text(encoding="utf-8")

    assert 'Офис (главный)' not in seed_account
    assert 'Филиал Центр' not in seed_demo
    assert 'Академгородок: пр. Академика Лаврентьева, д. 6' not in general_page
