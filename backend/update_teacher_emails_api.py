#!/usr/bin/env python3
"""
Задача 1 — Обновить email преподавателей.

Для каждого преподавателя, у которого email отсутствует или не содержит
транслитерацию фамилии, выполняет PUT /api/v1/teachers/{id} с полным
объектом преподавателя, в котором обновлено поле email.

Usage:
    python update_teacher_emails_api.py [--base-url URL] [--email EMAIL] [--password PASSWORD]

Defaults:
    --base-url  https://abc-language-school-production.up.railway.app
    --email     admin@abc-school.ru
    --password  admin123
"""

import argparse
import os
import sys
import urllib.request
import urllib.error
import json
from typing import Dict, List, Optional, Union

BASE_URL = "https://abc-language-school-production.up.railway.app"

# Canonical transliteration map for known surnames (lowercase)
KNOWN_SURNAMES: Dict[str, str] = {
    "Белова": "belova",
    "Арнгольд": "arngold",
    "Данилова": "danilova",
    "Евдокимова": "evdokimova",
    "Колесник": "kolesnik",
    "Куцых": "kutsykh",
    "Быковская": "bykovskaya",
    "Лукьянова": "lukyanova",
    "Митина": "mitina",
    "Осинина": "osinina",
    "Пасикан": "pasikan",
    "Переведенцева": "perevedentseva",
    "Позднякова": "pozdnyakova",
    "Рубе": "rube",
    "Винокурова": "vinokurova",
    "Темлякова": "temlyakova",
    "Федорова": "fedorova",
    "Фомина": "fomina",
}

# Standard Russian → Latin transliteration table
_TRANSLIT_TABLE: Dict[str, str] = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
    "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text: str) -> str:
    """Transliterate a Russian string to Latin lowercase."""
    result = []
    for char in text.lower():
        result.append(_TRANSLIT_TABLE.get(char, char))
    return "".join(result)


def get_email_for_teacher(full_name: str) -> str:
    """Return the canonical email for a teacher based on their surname."""
    parts = full_name.split()
    if not parts:
        return "unknown@abc-school.ru"
    surname = parts[0]
    translit = KNOWN_SURNAMES.get(surname) or transliterate(surname)
    return f"{translit}@abc-school.ru"


def email_needs_update(current_email: Optional[str], expected_email: str) -> bool:
    """Return True when the current email should be replaced by expected_email."""
    if not current_email:
        return True
    expected_local = expected_email.split("@")[0]
    current_local = current_email.split("@")[0] if "@" in current_email else current_email
    return current_local != expected_local


def _api_request(
    url: str,
    method: str = "GET",
    data: Optional[dict] = None,
    token: Optional[str] = None,
) -> Union[dict, list]:
    """Simple HTTP request helper using stdlib only."""
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason}: {body_text}") from e


def get_token(base_url: str, email: str, password: str) -> str:
    """Authenticate and return access token."""
    creds = {"email": email, "password": password}
    try:
        resp = _api_request(f"{base_url}/api/v1/auth/login", method="POST", data=creds)
        token = resp.get("access_token")  # type: ignore[union-attr]
        if token:
            print(f"✅ Authenticated as {email}")
            return token
    except RuntimeError as exc:
        print(f"⚠️  Auth failed for {email}: {exc}")

    raise SystemExit("❌ Could not authenticate.")


def get_teachers(base_url: str, token: str) -> List[dict]:
    """Return list of all teachers."""
    result = _api_request(f"{base_url}/api/v1/teachers", token=token)
    return result if isinstance(result, list) else []


def get_teacher(base_url: str, token: str, teacher_id: int) -> dict:
    """Return a single teacher's data by ID."""
    result = _api_request(f"{base_url}/api/v1/teachers/{teacher_id}", token=token)
    return result if isinstance(result, dict) else {}


def patch_teacher_email(base_url: str, token: str, teacher_id: int, email: str) -> None:
    """PUT the teacher's full object with updated email field."""
    teacher_data = get_teacher(base_url, token, teacher_id)
    if not teacher_data:
        raise RuntimeError(f"Teacher id={teacher_id} not found or returned empty data")
    teacher_data["email"] = email
    _api_request(
        f"{base_url}/api/v1/teachers/{teacher_id}",
        method="PUT",
        data=teacher_data,
        token=token,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Update teacher emails via API")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@abc-school.ru"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "admin123"))
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # Step 1: authenticate
    token = get_token(base_url, args.email, args.password)

    # Step 2: fetch all teachers
    teachers = get_teachers(base_url, token)
    print(f"ℹ️  Found {len(teachers)} teachers")

    # Step 3: update emails where needed
    updated = 0
    skipped = 0
    errors = 0

    for teacher in teachers:
        teacher_id = teacher.get("id")
        full_name = teacher.get("full_name", "")
        current_email = teacher.get("email")

        if not full_name:
            print(f"⚠️  Teacher id={teacher_id} has no full_name, skipping")
            skipped += 1
            continue

        expected_email = get_email_for_teacher(full_name)

        if email_needs_update(current_email, expected_email):
            try:
                patch_teacher_email(base_url, token, teacher_id, expected_email)
                print(
                    f"✅ Updated {full_name} (id={teacher_id}): "
                    f"{current_email!r} → {expected_email!r}"
                )
                updated += 1
            except RuntimeError as exc:
                print(f"❌ Failed to update {full_name} (id={teacher_id}): {exc}", file=sys.stderr)
                errors += 1
        else:
            print(f"⏭️  Skipping {full_name}: email already correct ({current_email!r})")
            skipped += 1

    print(f"\n✅ Done. Updated: {updated}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()
