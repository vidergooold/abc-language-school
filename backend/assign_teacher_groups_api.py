#!/usr/bin/env python3
"""
Задача 2 — Назначить группы преподавателям.

Получает список всех групп через GET /api/v1/groups.
Для каждой группы, у которой есть поле teacher_id, назначает группу
преподавателю через POST /api/v1/teachers/{teacher_id}/groups, предварительно
проверяя GET /api/v1/teachers/{id}/groups, чтобы не дублировать назначения.

Usage:
    python assign_teacher_groups_api.py [--base-url URL] [--email EMAIL] [--password PASSWORD]

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

BASE_URL = "https://abc-language-school-production.up.railway.app"


def _api_request(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    token: str | None = None,
) -> dict | list:
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


def get_groups(base_url: str, token: str) -> list[dict]:
    """Return list of all groups."""
    result = _api_request(f"{base_url}/api/v1/groups", token=token)
    return result if isinstance(result, list) else []


def get_teacher_group_ids(base_url: str, token: str, teacher_id: int) -> set[int]:
    """Return the set of group IDs already assigned to the teacher."""
    try:
        result = _api_request(f"{base_url}/api/v1/teachers/{teacher_id}/groups", token=token)
        entries = result if isinstance(result, list) else []
        return {entry["group_id"] for entry in entries if "group_id" in entry}
    except RuntimeError as exc:
        print(f"⚠️  Could not fetch groups for teacher id={teacher_id}: {exc}")
        return set()


def assign_group(base_url: str, token: str, teacher_id: int, group_id: int) -> None:
    """POST to assign group_id to teacher_id."""
    _api_request(
        f"{base_url}/api/v1/teachers/{teacher_id}/groups",
        method="POST",
        data={"group_id": group_id},
        token=token,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Assign groups to teachers via API")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", "admin@abc-school.ru"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD", "admin123"))
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # Step 1: authenticate
    token = get_token(base_url, args.email, args.password)

    # Step 2: fetch all groups
    groups = get_groups(base_url, token)
    print(f"ℹ️  Found {len(groups)} groups")

    # Step 3: assign groups that have a teacher_id
    assigned = 0
    skipped_no_teacher = 0
    skipped_already = 0
    errors = 0

    # Cache already-assigned groups per teacher to avoid redundant API calls
    teacher_group_cache: dict[int, set[int]] = {}

    for group in groups:
        group_id = group.get("id")
        group_name = group.get("name", f"id={group_id}")
        teacher_id = group.get("teacher_id")

        if not teacher_id:
            print(f"⏭️  Group '{group_name}' has no teacher_id, skipping")
            skipped_no_teacher += 1
            continue

        # Fetch existing assignments for this teacher (once per teacher)
        if teacher_id not in teacher_group_cache:
            teacher_group_cache[teacher_id] = get_teacher_group_ids(base_url, token, teacher_id)

        if group_id in teacher_group_cache[teacher_id]:
            print(
                f"⏭️  Group '{group_name}' already assigned to teacher id={teacher_id}, skipping"
            )
            skipped_already += 1
            continue

        try:
            assign_group(base_url, token, teacher_id, group_id)
            print(f"✅ Assigned group '{group_name}' (id={group_id}) to teacher id={teacher_id}")
            teacher_group_cache[teacher_id].add(group_id)
            assigned += 1
        except RuntimeError as exc:
            print(
                f"❌ Failed to assign group '{group_name}' (id={group_id}) "
                f"to teacher id={teacher_id}: {exc}",
                file=sys.stderr,
            )
            errors += 1

    print(
        f"\n✅ Done. Assigned: {assigned}, "
        f"Skipped (no teacher): {skipped_no_teacher}, "
        f"Skipped (already assigned): {skipped_already}, "
        f"Errors: {errors}"
    )


if __name__ == "__main__":
    main()
