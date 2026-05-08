"""merge heads

Revision ID: 476b21780d50
Revises: b20e835de97e, f1e2d3c4b5a6
Create Date: 2026-04-16 21:13:46.787169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '476b21780d50'
down_revision: Union[str, Sequence[str], None] = ('b20e835de97e', 'f1e2d3c4b5a6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
