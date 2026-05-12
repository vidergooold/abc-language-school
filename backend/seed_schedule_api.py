#!/usr/bin/env python3
"""
Seed recurring schedule lessons via the public API.

Dry run prints one planned lesson per line.
Real mode authenticates and POSTs every lesson to /api/v1/schedule.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, Sequence

BASE_URL = "https://abc-language-school-production.up.railway.app"
LESSONS_PER_TEACHER = 3

GROUP_IDS = {
    "FH1": 28,
    "AS2": 29,
    "AS1": 30,
    "HSK1": 31,
}
ENGLISH_GROUP_IDS = (GROUP_IDS["AS1"], GROUP_IDS["AS2"], GROUP_IDS["FH1"])
CHINESE_GROUP_ID = GROUP_IDS["HSK1"]
CHINESE_TEACHER_IDS = {35, 37, 39, 54, 55}
DEFAULT_TEACHER_IDS = tuple(range(32, 59))
DEFAULT_CLASSROOM_IDS = (1, 2, 3, 4)

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday")
SLOTS = (
    ("10:00:00", "11:30:00"),
    ("12:00:00", "13:30:00"),
    ("14:00:00", "15:30:00"),
    ("16:00:00", "17:30:00"),
)


class ApiError(RuntimeError):
    def __init__(self, status_code: int, reason: str, body: str):
        super().__init__(f"HTTP {status_code} {reason}: {body}")
        self.status_code = status_code
        self.reason = reason
        self.body = body


@dataclass(frozen=True)
class LessonPlan:
    teacher_id: int
    group_id: int
    classroom_id: int
    day_of_week: str
    time_start: str
    time_end: str
    lesson_date: str
    is_recurring: bool = True

    def to_payload(self) -> dict[str, object]:
        return {
            "group_id": self.group_id,
            "teacher_id": self.teacher_id,
            "classroom_id": self.classroom_id,
            "day_of_week": self.day_of_week,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "lesson_date": self.lesson_date,
            "is_recurring": self.is_recurring,
        }


def _api_request(
    url: str,
    *,
    method: str = "GET",
    data: dict[str, object] | None = None,
    token: str | None = None,
) -> dict | list:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise ApiError(exc.code, exc.reason, body_text) from exc


def get_token(base_url: str, email: str, password: str) -> str:
    response = _api_request(
        f"{base_url}/api/v1/auth/login",
        method="POST",
        data={"email": email, "password": password},
    )
    if not isinstance(response, dict) or not response.get("access_token"):
        raise SystemExit("❌ Не удалось получить access_token")
    return str(response["access_token"])


def fetch_teacher_ids(base_url: str, token: str) -> tuple[int, ...]:
    response = _api_request(f"{base_url}/api/v1/teachers", token=token)
    if not isinstance(response, list):
        raise SystemExit("❌ API вернул неожиданный ответ по /teachers")

    available_ids = sorted(
        int(item["id"])
        for item in response
        if isinstance(item, dict) and item.get("id") is not None
    )
    if len(available_ids) < len(DEFAULT_TEACHER_IDS):
        raise SystemExit(
            f"❌ Нужно минимум {len(DEFAULT_TEACHER_IDS)} активных преподавателей, найдено {len(available_ids)}"
        )

    if all(teacher_id in available_ids for teacher_id in DEFAULT_TEACHER_IDS):
        return DEFAULT_TEACHER_IDS

    return tuple(available_ids[: len(DEFAULT_TEACHER_IDS)])


def fetch_classroom_ids(base_url: str, token: str) -> tuple[int, ...]:
    response = _api_request(f"{base_url}/api/v1/classrooms", token=token)
    if not isinstance(response, list):
        raise SystemExit("❌ API вернул неожиданный ответ по /classrooms")

    classroom_ids = tuple(
        sorted(
            int(item["id"])
            for item in response
            if isinstance(item, dict) and item.get("id") is not None
        )
    )
    if not classroom_ids:
        raise SystemExit("❌ Не найдено ни одной активной аудитории")
    return classroom_ids


def _next_reference_monday(today: date | None = None) -> date:
    today = today or date.today()
    days_until_next_monday = (7 - today.weekday()) % 7 or 7
    return today + timedelta(days=days_until_next_monday)


def _slot_catalog() -> list[tuple[str, str, str, int, str]]:
    catalog: list[tuple[str, str, str, int, str]] = []
    for day_offset, day_name in enumerate(DAYS):
        for time_start, time_end in SLOTS:
            catalog.append((day_name, time_start, time_end, day_offset, f"{day_name}:{time_start}"))
    return catalog


def _preferred_group_ids(teacher_id: int, teacher_index: int) -> tuple[int, ...]:
    if teacher_id in CHINESE_TEACHER_IDS:
        return (CHINESE_GROUP_ID,) * LESSONS_PER_TEACHER

    return tuple(
        ENGLISH_GROUP_IDS[(teacher_index + lesson_index) % len(ENGLISH_GROUP_IDS)]
        for lesson_index in range(LESSONS_PER_TEACHER)
    )


def build_lessons(
    teacher_ids: Sequence[int] = DEFAULT_TEACHER_IDS,
    classroom_ids: Sequence[int] = DEFAULT_CLASSROOM_IDS,
    *,
    reference_monday: date | None = None,
) -> tuple[list[LessonPlan], list[str]]:
    if not classroom_ids:
        return [], ["⚠️  Нет доступных аудиторий"]

    anchor_monday = reference_monday or _next_reference_monday()
    slot_catalog = _slot_catalog()
    used_teacher_slots: set[tuple[int, str]] = set()
    used_group_slots: set[tuple[int, str, int]] = set()
    used_classroom_dates: set[tuple[int, str, str]] = set()
    lessons: list[LessonPlan] = []
    warnings: list[str] = []

    for teacher_index, teacher_id in enumerate(teacher_ids):
        for lesson_index, group_id in enumerate(_preferred_group_ids(teacher_id, teacher_index)):
            planned = False
            classroom_rotation = [
                classroom_ids[(teacher_index + lesson_index + offset) % len(classroom_ids)]
                for offset in range(len(classroom_ids))
            ]

            for slot_shift in range(len(slot_catalog)):
                slot = slot_catalog[(teacher_index * LESSONS_PER_TEACHER + lesson_index + slot_shift) % len(slot_catalog)]
                day_name, time_start, time_end, day_offset, slot_key = slot
                if (teacher_id, slot_key) in used_teacher_slots:
                    continue

                for week_offset in range(max(2, len(teacher_ids))):
                    if (group_id, slot_key, week_offset) in used_group_slots:
                        continue

                    lesson_date_value = (
                        datetime.combine(anchor_monday, datetime.min.time())
                        + timedelta(days=day_offset, weeks=week_offset)
                    ).isoformat()
                    date_key = lesson_date_value[:10]

                    for classroom_id in classroom_rotation:
                        if (classroom_id, date_key, time_start) in used_classroom_dates:
                            continue

                        plan = LessonPlan(
                            teacher_id=teacher_id,
                            group_id=group_id,
                            classroom_id=classroom_id,
                            day_of_week=day_name,
                            time_start=time_start,
                            time_end=time_end,
                            lesson_date=lesson_date_value,
                        )
                        lessons.append(plan)
                        used_teacher_slots.add((teacher_id, slot_key))
                        used_group_slots.add((group_id, slot_key, week_offset))
                        used_classroom_dates.add((classroom_id, date_key, time_start))
                        planned = True
                        break

                    if planned:
                        break

                if planned:
                    break

            if not planned:
                warnings.append(f"⚠️  Нет слотов для teacher_id={teacher_id}")

    return lessons, warnings


def format_lesson(plan: LessonPlan) -> str:
    return (
        f"teacher_id={plan.teacher_id} "
        f"group_id={plan.group_id} "
        f"classroom_id={plan.classroom_id} "
        f"day={plan.day_of_week} "
        f"time={plan.time_start}-{plan.time_end} "
        f"lesson_date={plan.lesson_date} "
        f"is_recurring={str(plan.is_recurring).lower()}"
    )


def create_lessons(base_url: str, token: str, lessons: Iterable[LessonPlan]) -> tuple[int, int, int]:
    created = 0
    skipped = 0
    errors = 0

    for plan in lessons:
        try:
            _api_request(
                f"{base_url}/api/v1/schedule",
                method="POST",
                data=plan.to_payload(),
                token=token,
            )
            created += 1
        except ApiError as exc:
            if exc.status_code == 409:
                skipped += 1
                print(f"⏭️  Конфликт: {format_lesson(plan)}")
                continue
            errors += 1
            print(f"❌ {format_lesson(plan)} -> {exc}", file=sys.stderr)

    return created, skipped, errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed recurring schedule lessons via API")
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", BASE_URL))
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@abc-school.ru"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "admin123"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    if args.dry_run:
        teacher_ids = DEFAULT_TEACHER_IDS
        classroom_ids = DEFAULT_CLASSROOM_IDS
    else:
        token = get_token(base_url, args.email, args.password)
        teacher_ids = fetch_teacher_ids(base_url, token)
        classroom_ids = fetch_classroom_ids(base_url, token)

    lessons, warnings = build_lessons(teacher_ids=teacher_ids, classroom_ids=classroom_ids)

    for warning in warnings:
        print(warning)

    if args.dry_run:
        for lesson in lessons:
            print(format_lesson(lesson))
        return

    created, skipped, errors = create_lessons(base_url, token, lessons)
    print(f"✅ Готово. Создано: {created}, Конфликт/пропуск: {skipped}, Ошибки: {errors}")


if __name__ == "__main__":
    main()
