from datetime import date

from seed_schedule_api import (
    CHINESE_GROUP_ID,
    CHINESE_TEACHER_IDS,
    DEFAULT_CLASSROOM_IDS,
    DEFAULT_TEACHER_IDS,
    LESSONS_PER_TEACHER,
    build_lessons,
    format_lesson,
)


def test_build_lessons_creates_three_lessons_per_teacher_without_warnings():
    lessons, warnings = build_lessons(
        teacher_ids=DEFAULT_TEACHER_IDS,
        classroom_ids=DEFAULT_CLASSROOM_IDS,
        reference_monday=date(2026, 5, 18),
    )

    assert len(lessons) == len(DEFAULT_TEACHER_IDS) * LESSONS_PER_TEACHER
    assert warnings == []

    counts_by_teacher: dict[int, int] = {}
    for lesson in lessons:
        counts_by_teacher[lesson.teacher_id] = counts_by_teacher.get(lesson.teacher_id, 0) + 1

    assert set(counts_by_teacher) == set(DEFAULT_TEACHER_IDS)
    assert set(counts_by_teacher.values()) == {LESSONS_PER_TEACHER}


def test_build_lessons_keeps_hsk1_for_allowed_teacher_ids_only():
    lessons, _ = build_lessons(
        teacher_ids=DEFAULT_TEACHER_IDS,
        classroom_ids=DEFAULT_CLASSROOM_IDS,
        reference_monday=date(2026, 5, 18),
    )

    for lesson in lessons:
        if lesson.group_id == CHINESE_GROUP_ID:
            assert lesson.teacher_id in CHINESE_TEACHER_IDS
        else:
            assert lesson.teacher_id not in CHINESE_TEACHER_IDS


def test_format_lesson_uses_api_friendly_time_format():
    lessons, _ = build_lessons(
        teacher_ids=DEFAULT_TEACHER_IDS,
        classroom_ids=DEFAULT_CLASSROOM_IDS,
        reference_monday=date(2026, 5, 18),
    )

    lines = [format_lesson(lesson) for lesson in lessons]

    assert len(lines) == 81
    assert all("⚠️" not in line for line in lines)
    assert all(":00-" in line or ":30-" in line for line in lines)
    assert all("is_recurring=true" in line for line in lines)
