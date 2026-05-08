import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DATABASE_URL", "postgresql://pytest_user:pytest_pass@invalid:5432/pytest_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
