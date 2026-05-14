from datetime import date, time

from app.schedule_rules import (
    canonical_program_duration_minutes,
    derive_time_end,
    is_non_study_date,
)
from seed_real_schedule import _lesson_duration_minutes
from seed_requirements import TARGET_LESSONS_PER_TEACHER


def test_canonical_program_duration_mapping():
    assert canonical_program_duration_minutes("Дошкольники") == 45
    assert canonical_program_duration_minutes("FH1") == 50
    assert canonical_program_duration_minutes("AS3") == 60
    assert canonical_program_duration_minutes("GWA2") == 75
    assert canonical_program_duration_minutes("GWB2+") == 90
    assert canonical_program_duration_minutes("Взрослые групповые") == 90
    assert canonical_program_duration_minutes("Мини-группа") == 45
    assert canonical_program_duration_minutes("Индивидуальные занятия") == 45
    assert canonical_program_duration_minutes("Китайский язык") == 45


def test_time_end_is_derived_from_program_duration():
    assert derive_time_end(time(9, 0), 45) == time(9, 45)
    assert derive_time_end(time(10, 0), 50) == time(10, 50)
    assert derive_time_end(time(13, 0), 60) == time(14, 0)
    assert derive_time_end(time(15, 0), 75) == time(16, 15)
    assert derive_time_end(time(18, 0), 90) == time(19, 30)


def test_non_study_periods_repeat_annually():
    assert is_non_study_date(date(2026, 6, 1))
    assert is_non_study_date(date(2026, 8, 31))
    assert not is_non_study_date(date(2026, 9, 1))

    assert is_non_study_date(date(2026, 12, 30))
    assert is_non_study_date(date(2027, 1, 7))
    assert not is_non_study_date(date(2027, 1, 8))

    assert is_non_study_date(date(2026, 11, 4))
    assert is_non_study_date(date(2026, 2, 23))
    assert is_non_study_date(date(2026, 3, 8))
    assert is_non_study_date(date(2026, 5, 1))
    assert is_non_study_date(date(2026, 5, 9))

    assert not is_non_study_date(date(2026, 10, 28))  # Осенние каникулы не блокируются
    assert not is_non_study_date(date(2026, 3, 25))   # Весенние каникулы не блокируются


def test_seed_duration_mapping_and_minimum_lessons_target():
    assert _lesson_duration_minutes("FH1") == 50
    assert _lesson_duration_minutes("Мини-группа (2 чел.)") == 45
    assert _lesson_duration_minutes("Китайский") == 45
    assert TARGET_LESSONS_PER_TEACHER == 5
