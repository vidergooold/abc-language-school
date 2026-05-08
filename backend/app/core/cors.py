"""CORS origin helper — read allowed origins from env vars."""
import os


def get_cors_origins() -> list[str]:
    """Return allowed CORS origins from env, with local-dev defaults.

    Reads origins from the ``ALLOWED_ORIGINS`` environment variable (preferred).
    Falls back to ``FRONTEND_URL`` for backward compatibility.

    Set ``ALLOWED_ORIGINS`` to a comma-separated list of origins, e.g.::

        ALLOWED_ORIGINS=https://abc-school-frontend.vercel.app,https://www.abc-school.ru

    Falls back to ``localhost:5173`` and ``localhost:3000`` when neither
    variable is set so that local development works without a ``.env`` file.

    Note: ``allow_origins=["*"]`` is intentionally avoided because browsers
    reject that combination when ``allow_credentials=True`` is also set.
    """
    env_val = (
        os.getenv("ALLOWED_ORIGINS", "").strip()
        or os.getenv("FRONTEND_URL", "").strip()
    )
    origins = [o.strip() for o in env_val.split(",") if o.strip()] if env_val else []
    defaults = ["http://localhost:5173", "http://localhost:3000"]
    # Preserve order; deduplicate while keeping first occurrence
    return list(dict.fromkeys(origins + defaults))
