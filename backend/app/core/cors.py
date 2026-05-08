"""CORS origin helper — read allowed origins from the FRONTEND_URL env var."""
import os


def get_cors_origins() -> list[str]:
    """Return allowed CORS origins from env, with local-dev defaults.

    Set ``FRONTEND_URL`` to a comma-separated list of origins, e.g.::

        FRONTEND_URL=https://abc-school-frontend.vercel.app

    Falls back to ``localhost:5173`` and ``localhost:3000`` when the variable
    is unset so that local development works without a ``.env`` file.

    Note: ``allow_origins=["*"]`` is intentionally avoided because browsers
    reject that combination when ``allow_credentials=True`` is also set.
    """
    env_val = os.getenv("FRONTEND_URL", "").strip()
    origins = [o.strip() for o in env_val.split(",") if o.strip()] if env_val else []
    defaults = ["http://localhost:5173", "http://localhost:3000"]
    # Preserve order; deduplicate while keeping first occurrence
    return list(dict.fromkeys(origins + defaults))
