import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_BRANCHES = {
    "Гимназия 11 «Гармония»",
    "Гимназия №7 «Сибирская»",
    "МАОУ ЛИТ",
    "МАОУ НГПЛ",
    "МАОУ НЭЛ",
    "МАОУ СОШ №216",
    "МАОУ СОШ №217",
    "МАОУ СОШ №218",
    "МАОУ СОШ №221",
    "МАОУ СОШ №222",
    "МБОУ Гимназия №5",
    "МБОУ Гимназия №9",
    "МБОУ СОШ №11",
    "МБОУ СОШ №121 «Академическая»",
    "МБОУ СОШ №13",
    "МБОУ СОШ №155",
    "МБОУ СОШ №167",
    "МБОУ СОШ №186",
    "МБОУ СОШ №188",
    "МБОУ СОШ №195",
    "МБОУ СОШ №56",
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


def _parse_migration_allowed_branches() -> set[str]:
    source = (
        ROOT / "backend/alembic/versions/e1f2a3b4c5d6_normalize_canonical_branch_teacher_classroom_data.py"
    ).read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "_ALLOWED_BRANCHES" for target in node.targets)
        ):
            return set(ast.literal_eval(node.value))
    raise AssertionError("_ALLOWED_BRANCHES constant not found in migration")


def test_seed_sources_only_keep_canonical_branches():
    assert _parse_seed_branches() == ALLOWED_BRANCHES
    assert _parse_sql_branch_names() == ALLOWED_BRANCHES


def test_migration_allows_only_canonical_branches():
    assert _parse_migration_allowed_branches() == ALLOWED_BRANCHES


def test_old_branch_names_removed_from_hardcode_sources():
    source_bundle = "\n".join(
        [
            (ROOT / "backend/seed_account_data.py").read_text(encoding="utf-8"),
            (ROOT / "backend/seed_demo.py").read_text(encoding="utf-8"),
            (ROOT / "frontend/src/pages/organization/General.vue").read_text(encoding="utf-8"),
        ]
    )

    obsolete_fragments = {
        "Офис",
        "Филиал в ",
        "МБОУ СОШ №2",
        "МБОУ СОШ №199",
        "МБОУ СОШ № 61 им. Н.М.Иванова",
    }
    for fragment in obsolete_fragments:
        assert fragment not in source_bundle, f"Obsolete branch fragment '{fragment}' found"
