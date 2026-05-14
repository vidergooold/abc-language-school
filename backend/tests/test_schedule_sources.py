import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from seed_real_schedule import BRANCH_CLASSROOMS, GROUPS_SCHEDULE, ALLOWED_TEACHER_LASTNAMES

CHINESE_TEACHER_LASTNAMES = {"Винокурова", "Воронцова"}


CANONICAL_BRANCH_CLASSROOMS = {
    "МАОУ Гимназия №11 «Гармония»": {"каб. 113", "каб. 114"},
    "МАОУ Гимназия №7 «Сибирская»": {"каб. 119"},
    "МАОУ ЛИТ": {"каб. библ.", "каб. 116"},
    "МАОУ НГПЛ": {"каб. 205"},
    "МАОУ НЭЛ": {"каб. 312"},
    "МАОУ СОШ №216": {"каб. 317", "каб. 410"},
    "МАОУ СОШ №217": {"каб. 314А"},
    "МАОУ СОШ №218": {"каб. АВС"},
    "МАОУ СОШ №222": {"каб. 128", "каб. 311"},
    "МБОУ Гимназия №5": {"каб. 191"},
    "МБОУ Гимназия №9": {"каб. 37", "каб. 41"},
    "МБОУ СОШ №11": {"каб. 203"},
    "МБОУ СОШ №121 «Академическая»": {"каб. 214"},
    "МБОУ СОШ №155": {"каб. 426"},
    "МБОУ СОШ №186": {"каб. 211"},
    "МБОУ СОШ №188": {"каб. 409", "каб. АВС"},
    "МБОУ СОШ №195": {"каб. 415"},
    "МБОУ СОШ №56": {"каб. 3", "каб. 10"},
}


def test_branch_classroom_mapping_is_canonical():
    assert {branch: set(classrooms) for branch, classrooms in BRANCH_CLASSROOMS.items()} == CANONICAL_BRANCH_CLASSROOMS


def test_schedule_uses_only_canonical_branch_classroom_links_and_teachers():
    assert GROUPS_SCHEDULE, "GROUPS_SCHEDULE must not be empty"

    for entry in GROUPS_SCHEDULE:
        assert "branch_name" in entry and entry["branch_name"] in CANONICAL_BRANCH_CLASSROOMS
        assert entry["classroom"] in CANONICAL_BRANCH_CLASSROOMS[entry["branch_name"]]
        assert entry["teacher_lastname"] in ALLOWED_TEACHER_LASTNAMES


def test_removed_old_classrooms_not_present_in_schedule():
    obsolete_classrooms = {
        "Кабинет 101",
        "Кабинет 102",
        "Кабинет 103",
        "Кабинет 201",
        "Кабинет 202",
        "Кабинет 203",
        "Кабинет 204",
    }

    used_classrooms = {entry["classroom"] for entry in GROUPS_SCHEDULE}
    assert not used_classrooms.intersection(obsolete_classrooms)


def test_chinese_groups_are_taught_only_by_canonical_chinese_teachers():
    chinese_entries = [entry for entry in GROUPS_SCHEDULE if entry["group_name"] == "Китайский"]
    assert chinese_entries, "GROUPS_SCHEDULE must include 'Китайский' entries"
    for entry in chinese_entries:
        assert entry.get("language") == "Китайский"
        assert entry["teacher_lastname"] in CHINESE_TEACHER_LASTNAMES


def test_canonical_chinese_teachers_not_assigned_to_non_chinese_groups():
    for entry in GROUPS_SCHEDULE:
        if entry["group_name"] == "Китайский":
            continue
        assert entry["teacher_lastname"] not in CHINESE_TEACHER_LASTNAMES
