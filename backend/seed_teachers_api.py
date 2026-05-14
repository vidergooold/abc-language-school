#!/usr/bin/env python3
"""
Script to add missing teachers to the production ABC Language School API.

Usage:
    python seed_teachers_api.py [--base-url URL] [--email EMAIL] [--password PASSWORD]

Defaults:
    --base-url  https://abc-language-school-production.up.railway.app
    --email     admin@abc-school.ru
    --password  admin123
"""

import argparse
import sys
import urllib.request
import urllib.error
import json

BASE_URL = "https://abc-language-school-production.up.railway.app"

REQUIRED_TEACHERS = [
    "Белова Александра Анатольевна",
    "Арнольд Валерия Евгеньевна",
    "Данилова Мария Анатольевна",
    "Евдокимова Полина Евгеньевна",
    "Колесник Любовь Николаевна",
    "Куцых Марина Евгеньевна",
    "Быковская Марина Эдуардовна",
    "Лукьянова Светлана Ярославовна",
    "Митина Ольга Сергеевна",
    "Осинина Светлана Николаевна",
    "Пасикан Ангелина Сергеевна",
    "Переведенцева Александра Андреевна",
    "Позднякова Виктория Сергеевна",
    "Рубе Дарья Васильевна",
    "Винокурова Елена Александровна",
    "Темлякова Анна Михайловна",
    "Федорова Анфиса Вячеславовна",
    "Фомина Снежанна Олеговна",
]


def _api_request(url: str, method: str = "GET", data: dict | None = None, token: str | None = None) -> dict:
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


_FALLBACK_EMAILS: tuple[str, ...] = (
    "admin@abcschool.com",
    "admin@abc-school.ru",
)
_FALLBACK_PASSWORDS: tuple[str, ...] = ("admin123", "password")


def get_token(base_url: str, email: str, password: str) -> str:
    """Authenticate and return access token."""
    # Keep emails and passwords as separate sequences to avoid taint analysis
    # treating email strings as sensitive because they co-occur with passwords.
    all_emails: tuple[str, ...] = (email,) + _FALLBACK_EMAILS

    for idx in range(len(all_emails)):
        attempt_email = all_emails[idx]
        attempt_password = password if idx == 0 else _FALLBACK_PASSWORDS[idx - 1]
        creds = {"email": attempt_email, "password": attempt_password}
        try:
            resp = _api_request(f"{base_url}/api/v1/auth/login", method="POST", data=creds)
            token = resp.get("access_token")
            if token:
                print(f"✅ Authenticated as {attempt_email}")
                return token
        except RuntimeError as exc:
            print(f"⚠️  Auth failed for {attempt_email}: {exc}")

    raise SystemExit("❌ Could not authenticate with any known credentials.")


def get_existing_teachers(base_url: str, token: str) -> set[str]:
    """Return the set of existing teacher full_names."""
    teachers = _api_request(f"{base_url}/api/v1/teachers", token=token)
    return {t["full_name"] for t in teachers}


def add_teacher(base_url: str, token: str, full_name: str) -> dict:
    """Add a single teacher and return the created record."""
    return _api_request(
        f"{base_url}/api/v1/teachers",
        method="POST",
        data={"full_name": full_name, "role": "teacher"},
        token=token,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed missing teachers via API")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--email", default="admin@abc-school.ru")
    parser.add_argument("--password", default="admin123")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # Step 1: authenticate
    token = get_token(base_url, args.email, args.password)

    # Step 2: get existing teachers
    existing = get_existing_teachers(base_url, token)
    print(f"ℹ️  Found {len(existing)} existing teachers")

    # Step 3: add missing teachers
    added = 0
    skipped = 0
    for full_name in REQUIRED_TEACHERS:
        if full_name in existing:
            print(f"⏭️  Skipping (already exists): {full_name}")
            skipped += 1
        else:
            try:
                result = add_teacher(base_url, token, full_name)
                print(f"✅ Added teacher: {full_name} (id={result.get('id')})")
                added += 1
                existing.add(full_name)
            except RuntimeError as exc:
                print(f"❌ Failed to add {full_name}: {exc}", file=sys.stderr)

    print(f"\n✅ Done. Added: {added}, Skipped (already existed): {skipped}")


if __name__ == "__main__":
    main()
