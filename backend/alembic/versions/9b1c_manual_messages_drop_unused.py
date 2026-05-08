"""manual messages and drop unused tables

Revision ID: 9b1c_manual_messages_drop_unused
Revises: e2f3a4b5c6d7
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "9b1c_manual_messages_drop_unused"
down_revision = "e2f3a4b5c6d7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("recipient_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_messages_id", "messages", ["id"], unique=False)

    op.execute("DROP TABLE IF EXISTS discounts CASCADE")
    op.execute("DROP TABLE IF EXISTS waitlist CASCADE")


def downgrade():
    op.drop_index("ix_messages_id", table_name="messages")
    op.drop_table("messages")
