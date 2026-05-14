from datetime import date, datetime, time, timedelta
from typing import Optional


CANONICAL_PROGRAM_DURATION_MINUTES = {
    "дошкольники": 45,
    "fh1": 50,
    "as1": 50,
    "as2": 60,
    "as3": 60,
    "as4": 60,
    "gwa1+": 75,
    "gwa2": 75,
    "gwb1": 90,
    "gwb1+": 90,
    "gwb2": 90,
    "gwb2+": 90,
    "gwc1": 90,
    "взрослые групповые": 90,
    "мини-группа": 45,
    "мини-группа (2 чел.)": 45,
    "индивидуальные занятия": 45,
    "китайский": 45,
    "китайский язык": 45,
}

FIXED_NON_STUDY_DATES = {
    (2, 23),
    (3, 8),
    (5, 1),
    (5, 9),
    (11, 4),
}


def normalize_program_key(name: Optional[str]) -> str:
    return (name or "").strip().lower().replace("ё", "е")


def canonical_program_duration_minutes(program_name: Optional[str]) -> Optional[int]:
    key = normalize_program_key(program_name)
    if not key:
        return None
    if key in CANONICAL_PROGRAM_DURATION_MINUTES:
        return CANONICAL_PROGRAM_DURATION_MINUTES[key]
    if key.startswith("мини-группа"):
        return CANONICAL_PROGRAM_DURATION_MINUTES["мини-группа"]
    if "," in key:
        matched = {
            CANONICAL_PROGRAM_DURATION_MINUTES[part]
            for part in (token.strip() for token in key.split(","))
            if part in CANONICAL_PROGRAM_DURATION_MINUTES
        }
        if len(matched) == 1:
            return next(iter(matched))
    return None


def derive_time_end(time_start: time, duration_minutes: int) -> time:
    return (
        datetime.combine(date.today(), time_start) + timedelta(minutes=duration_minutes)
    ).time().replace(second=0, microsecond=0)


def is_non_study_date(lesson_date: date) -> bool:
    month_day = (lesson_date.month, lesson_date.day)
    if month_day in FIXED_NON_STUDY_DATES:
        return True
    if lesson_date.month in (6, 7, 8):
        return True
    if (lesson_date.month == 12 and lesson_date.day >= 30) or (
        lesson_date.month == 1 and lesson_date.day <= 7
    ):
        return True
    return False
