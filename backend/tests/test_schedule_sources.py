from seed_real_schedule import BRANCH_CLASSROOMS, GROUPS_SCHEDULE, ALLOWED_TEACHER_LASTNAMES


CANONICAL_BRANCH_CLASSROOMS = {
    "Гимназия 11 «Гармония»": {"каб. 113", "каб. 114"},
    "Гимназия №7 «Сибирская»": {"каб. 119"},
    "МАОУ ЛИТ": {"каб. библиотека", "каб. 116"},
    "МАОУ НГПЛ": {"каб. 115"},
    "МАОУ НЭЛ": {"каб. 205"},
    "МАОУ СОШ №216": {"каб. 317", "каб. 410"},
    "МАОУ СОШ №217": {"каб. 314А"},
    "МАОУ СОШ №218": {"каб. АВС"},
    "МАОУ СОШ №221": {"каб. 128", "каб. 311"},
    "МАОУ СОШ №222": {"каб. 128", "каб. 311"},
    "МБОУ Гимназия №5": {"каб. 191"},
    "МБОУ Гимназия №9": {"каб. 37", "каб. 41"},
    "МБОУ СОШ №11": {"каб. 203"},
    "МБОУ СОШ №121 «Академическая»": {"каб. 214"},
    "МБОУ СОШ №13": {"каб. 18"},
    "МБОУ СОШ №155": {"каб. 426"},
    "МБОУ СОШ №167": {"каб. 211"},
    "МБОУ СОШ №186": {"каб. 211"},
    "МБОУ СОШ №188": {"каб. 409", "каб. АВС"},
    "МБОУ СОШ №195": {"каб. 229"},
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
