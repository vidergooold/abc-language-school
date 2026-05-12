"""
Patch script: update language and program_name for existing groups.

Usage:
    DATABASE_URL=postgresql+asyncpg://... python patch_group_language.py
or
    DATABASE_URL=postgresql://... python patch_group_language.py
"""

import asyncio
import os
import sys


UPDATES = [
    (28, "Английский", "FH1"),
    (29, "Английский", "AS2"),
    (30, "Английский", "AS1"),
    (31, "Китайский",  "HSK1"),
]


async def run_async(database_url: str) -> None:
    try:
        import asyncpg
    except ImportError:
        print("asyncpg not installed, falling back to psycopg2")
        return run_sync(database_url)

    # Strip +asyncpg or +psycopg2 scheme suffix for asyncpg
    url = database_url
    for prefix in ("postgresql+asyncpg://", "postgres+asyncpg://"):
        if url.startswith(prefix):
            url = "postgresql://" + url[len(prefix):]
            break

    conn = await asyncpg.connect(url)
    try:
        for group_id, language, program_name in UPDATES:
            result = await conn.execute(
                "UPDATE groups SET language=$1, program_name=$2 WHERE id=$3",
                language, program_name, group_id,
            )
            print(f"  id={group_id}: {result}")
    finally:
        await conn.close()


def run_sync(database_url: str) -> None:
    import psycopg2

    # Strip async driver prefix if present
    url = database_url
    for prefix in ("postgresql+asyncpg://", "postgres+asyncpg://",
                   "postgresql+psycopg2://", "postgres+psycopg2://"):
        if url.startswith(prefix):
            url = "postgresql://" + url[len(prefix):]
            break

    conn = psycopg2.connect(url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for group_id, language, program_name in UPDATES:
                cur.execute(
                    "UPDATE groups SET language=%s, program_name=%s WHERE id=%s",
                    (language, program_name, group_id),
                )
                print(f"  id={group_id}: {cur.rowcount} row(s) updated")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    print("Patching groups language/program_name...")

    # Use async path if asyncpg is available and URL looks like postgres
    if "postgresql" in database_url or "postgres" in database_url:
        try:
            import asyncpg  # noqa: F401
            asyncio.run(run_async(database_url))
        except ImportError:
            run_sync(database_url)
    else:
        print(f"Unsupported DATABASE_URL scheme: {database_url}", file=sys.stderr)
        sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()
