"""add_all_missing_tables

Creates every table that has a SQLAlchemy model but no prior CREATE TABLE
in the migration chain.

Missing tables (in FK-dependency order):
  teachers, classrooms, student_groups, invoices, documents,
  audit_log, child_forms, adult_forms, preschool_forms, teacher_forms,
  testing_forms, feedback_forms, tax_forms, notification_queue,
  report_cache, room_bookings, enrollment_status_history

Revision ID: a0b1c2d3e4f5
Revises: 9b1c_manual_messages_drop_unused
Create Date: 2026-05-08 08:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, Sequence[str], None] = "9b1c_manual_messages_drop_unused"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _type_exists(type_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT 1 FROM pg_type WHERE typname = :tname"
        ),
        {"tname": type_name},
    )
    return result.scalar() is not None


def upgrade() -> None:
    # ── Ensure new enum types exist ────────────────────────────────────────
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE bookingpurpose AS ENUM "
        "    ('lesson','exam','event','consultation','staff','maintenance'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE bookingstatus AS ENUM "
        "    ('pending','confirmed','cancelled','completed'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$"
    )
    op.execute(
        "DO $$ BEGIN "
        "  CREATE TYPE documentcategory AS ENUM "
        "    ('policy','schedule','template','contract','receipt','other'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; "
        "END $$"
    )

    # paymentstatus already exists but Invoice uses different values.
    for v in ("paid", "partial", "overdue"):
        op.execute(
            f"ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS '{v}'"
        )

    # ── 1. teachers ────────────────────────────────────────────────────────
    if not _table_exists("teachers"):
        op.create_table(
            "teachers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("phone", sa.String(length=50), nullable=True),
            sa.Column("subject", sa.String(length=100), nullable=True),
            sa.Column("language_level", sa.String(length=50), nullable=True),
            sa.Column("experience_years", sa.Integer(), nullable=True),
            sa.Column("bio", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("hired_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
        )
        op.create_index(op.f("ix_teachers_id"), "teachers", ["id"], unique=False)

    # ── 2. classrooms ──────────────────────────────────────────────────────
    if not _table_exists("classrooms"):
        op.create_table(
            "classrooms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("capacity", sa.Integer(), nullable=True),
            sa.Column("floor", sa.Integer(), nullable=True),
            sa.Column("has_projector", sa.Boolean(), nullable=True),
            sa.Column("has_whiteboard", sa.Boolean(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_classrooms_id"), "classrooms", ["id"], unique=False)

    # ── 3. student_groups ──────────────────────────────────────────────────
    if not _table_exists("student_groups"):
        op.create_table(
            "student_groups",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("student_name", sa.String(length=255), nullable=False),
            sa.Column("student_phone", sa.String(length=50), nullable=True),
            sa.Column("student_email", sa.String(length=255), nullable=True),
            sa.Column("student_type", sa.String(length=50), nullable=False),
            sa.Column("form_id", sa.Integer(), nullable=True),
            sa.Column("enrolled_at", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_student_groups_id"), "student_groups", ["id"], unique=False)

    # ── 4. invoices ────────────────────────────────────────────────────────
    if not _table_exists("invoices"):
        op.create_table(
            "invoices",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("group_id", sa.Integer(), nullable=False),
            sa.Column("student_group_id", sa.Integer(), nullable=True),
            sa.Column("student_name", sa.String(length=255), nullable=False),
            sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("amount_paid", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("period", sa.String(length=20), nullable=False),
            sa.Column("due_date", sa.DateTime(), nullable=False),
            sa.Column(
                "status",
                sa.Enum(
                    "pending", "paid", "partial", "overdue", "refunded",
                    name="paymentstatus",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
            sa.ForeignKeyConstraint(["student_group_id"], ["student_groups.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)

    # ── 5. documents ───────────────────────────────────────────────────────
    if not _table_exists("documents"):
        op.create_table(
            "documents",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("description", sa.String(length=512), nullable=True),
            sa.Column("file_url", sa.String(length=512), nullable=False),
            sa.Column(
                "category",
                sa.Enum(
                    "policy", "schedule", "template", "contract", "receipt", "other",
                    name="documentcategory",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    # ── 6. audit_log ───────────────────────────────────────────────────────
    if not _table_exists("audit_log"):
        op.create_table(
            "audit_log",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_email", sa.String(length=255), nullable=True),
            sa.Column("user_role", sa.String(length=50), nullable=True),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("entity_type", sa.String(length=100), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=True),
            sa.Column("http_method", sa.String(length=10), nullable=True),
            sa.Column("endpoint", sa.String(length=500), nullable=True),
            sa.Column("status_code", sa.Integer(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.Column("user_agent", sa.String(length=500), nullable=True),
            sa.Column("ip_address", sa.String(length=50), nullable=True),
            sa.Column("request_body", sa.Text(), nullable=True),
            sa.Column("old_value", sa.Text(), nullable=True),
            sa.Column("new_value", sa.Text(), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_audit_log_id"), "audit_log", ["id"], unique=False)
        op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"], unique=False)
        op.create_index("ix_audit_log_action", "audit_log", ["action"], unique=False)
        op.create_index("ix_audit_log_entity_type", "audit_log", ["entity_type"], unique=False)
        op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"], unique=False)
        op.create_index("ix_audit_entity", "audit_log", ["entity_type", "entity_id"], unique=False)
        op.create_index("ix_audit_user_time", "audit_log", ["user_id", "created_at"], unique=False)

    # ── 7. child_forms ─────────────────────────────────────────────────────
    if not _table_exists("child_forms"):
        op.create_table(
            "child_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("fio", sa.String(), nullable=False),
            sa.Column("age", sa.String(), nullable=True),
            sa.Column("birthdate", sa.String(), nullable=True),
            sa.Column("school", sa.String(), nullable=False),
            sa.Column("grade", sa.String(), nullable=False),
            sa.Column("shift", sa.String(), nullable=True),
            sa.Column("extended", sa.Boolean(), nullable=True),
            sa.Column("parent_fio", sa.String(), nullable=False),
            sa.Column("parent_work", sa.Text(), nullable=True),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("address", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("studied_before", sa.String(), nullable=True),
            sa.Column("where_how", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_child_forms_id"), "child_forms", ["id"], unique=False)

    # ── 8. adult_forms ─────────────────────────────────────────────────────
    if not _table_exists("adult_forms"):
        op.create_table(
            "adult_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("fio", sa.String(), nullable=False),
            sa.Column("age", sa.String(), nullable=True),
            sa.Column("birthdate", sa.String(), nullable=True),
            sa.Column("work", sa.Text(), nullable=True),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("address", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("studied_before", sa.String(), nullable=True),
            sa.Column("where_how", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_adult_forms_id"), "adult_forms", ["id"], unique=False)

    # ── 9. preschool_forms ─────────────────────────────────────────────────
    if not _table_exists("preschool_forms"):
        op.create_table(
            "preschool_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("fio", sa.String(), nullable=False),
            sa.Column("age", sa.String(), nullable=True),
            sa.Column("birthdate", sa.String(), nullable=True),
            sa.Column("kindergarten", sa.String(), nullable=False),
            sa.Column("group", sa.String(), nullable=False),
            sa.Column("parent_fio", sa.String(), nullable=False),
            sa.Column("parent_work", sa.Text(), nullable=True),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("address", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("pickup_time", sa.String(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_preschool_forms_id"), "preschool_forms", ["id"], unique=False)

    # ── 10. teacher_forms ──────────────────────────────────────────────────
    if not _table_exists("teacher_forms"):
        op.create_table(
            "teacher_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("fio", sa.String(), nullable=False),
            sa.Column("birth_info", sa.Text(), nullable=False),
            sa.Column("marital_status", sa.String(), nullable=False),
            sa.Column("education", sa.Text(), nullable=False),
            sa.Column("work_experience", sa.Text(), nullable=False),
            sa.Column("language_level", sa.String(), nullable=False),
            sa.Column("skills", sa.Text(), nullable=True),
            sa.Column("qualities", sa.Text(), nullable=True),
            sa.Column("address", sa.String(), nullable=False),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_teacher_forms_id"), "teacher_forms", ["id"], unique=False)

    # ── 11. testing_forms ──────────────────────────────────────────────────
    if not _table_exists("testing_forms"):
        op.create_table(
            "testing_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("fio", sa.String(), nullable=False),
            sa.Column("age", sa.String(), nullable=False),
            sa.Column("school", sa.String(), nullable=False),
            sa.Column("grade", sa.String(), nullable=False),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("test_level", sa.String(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_testing_forms_id"), "testing_forms", ["id"], unique=False)

    # ── 12. feedback_forms ─────────────────────────────────────────────────
    if not _table_exists("feedback_forms"):
        op.create_table(
            "feedback_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("phone", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_feedback_forms_id"), "feedback_forms", ["id"], unique=False)

    # ── 13. tax_forms ──────────────────────────────────────────────────────
    if not _table_exists("tax_forms"):
        op.create_table(
            "tax_forms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("payer_fio", sa.String(), nullable=False),
            sa.Column("payer_inn", sa.String(), nullable=False),
            sa.Column("payer_birthdate", sa.String(), nullable=False),
            sa.Column("payer_passport_series", sa.String(), nullable=False),
            sa.Column("payer_passport_number", sa.String(), nullable=False),
            sa.Column("payer_passport_date", sa.String(), nullable=False),
            sa.Column("payer_department_code", sa.String(), nullable=False),
            sa.Column("payer_phone", sa.String(), nullable=False),
            sa.Column("student_fio", sa.String(), nullable=False),
            sa.Column("student_inn", sa.String(), nullable=True),
            sa.Column("student_birthdate", sa.String(), nullable=False),
            sa.Column("student_doc_type", sa.String(), nullable=False),
            sa.Column("student_doc_series", sa.String(), nullable=False),
            sa.Column("student_doc_number", sa.String(), nullable=False),
            sa.Column("student_doc_date", sa.String(), nullable=False),
            sa.Column("period", sa.String(), nullable=False),
            sa.Column("cost", sa.String(), nullable=True),
            sa.Column("has_contracts", sa.String(), nullable=False),
            sa.Column("delivery_method", sa.String(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_tax_forms_id"), "tax_forms", ["id"], unique=False)

    # ── 14. notification_queue ─────────────────────────────────────────────
    if not _table_exists("notification_queue"):
        op.create_table(
            "notification_queue",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("notification_id", sa.Integer(), nullable=True),
            sa.Column("recipient_email", sa.String(length=255), nullable=True),
            sa.Column("recipient_phone", sa.String(length=50), nullable=True),
            sa.Column("recipient_name", sa.String(length=255), nullable=True),
            sa.Column("subject", sa.String(length=255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column(
                "channel",
                sa.Enum(
                    "email", "sms", "telegram", "internal",
                    name="notificationchannel",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("scheduled_at", sa.DateTime(), nullable=False),
            sa.Column(
                "status",
                sa.Enum(
                    "pending", "sent", "failed", "cancelled",
                    name="notificationstatus",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
            sa.Column("retry_count", sa.Integer(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_notification_queue_id"), "notification_queue", ["id"], unique=False
        )

    # ── 15. report_cache ───────────────────────────────────────────────────
    if not _table_exists("report_cache"):
        op.create_table(
            "report_cache",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("report_type", sa.String(length=100), nullable=False),
            sa.Column("period", sa.String(length=20), nullable=True),
            sa.Column("params_hash", sa.String(length=64), nullable=True),
            sa.Column("data", sa.JSON(), nullable=False),
            sa.Column("generated_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_report_cache_id"), "report_cache", ["id"], unique=False)
        op.create_index(
            "ix_report_cache_report_type", "report_cache", ["report_type"], unique=False
        )
        op.create_index("ix_report_cache_period", "report_cache", ["period"], unique=False)

    # ── 16. room_bookings ──────────────────────────────────────────────────
    if not _table_exists("room_bookings"):
        op.create_table(
            "room_bookings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("classroom_id", sa.Integer(), nullable=False),
            sa.Column("booked_by_user_id", sa.Integer(), nullable=True),
            sa.Column("teacher_id", sa.Integer(), nullable=True),
            sa.Column("booking_date", sa.Date(), nullable=False),
            sa.Column("time_start", sa.Time(), nullable=False),
            sa.Column("time_end", sa.Time(), nullable=False),
            sa.Column(
                "purpose",
                sa.Enum(
                    "lesson", "exam", "event", "consultation", "staff", "maintenance",
                    name="bookingpurpose",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column(
                "status",
                sa.Enum(
                    "pending", "confirmed", "cancelled", "completed",
                    name="bookingstatus",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("expected_attendees", sa.Integer(), nullable=True),
            sa.Column("is_recurring", sa.Boolean(), nullable=True),
            sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
            sa.Column("parent_booking_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("confirmed_at", sa.DateTime(), nullable=True),
            sa.Column("cancelled_at", sa.DateTime(), nullable=True),
            sa.Column("cancel_reason", sa.Text(), nullable=True),
            sa.CheckConstraint("time_start < time_end", name="ck_room_bookings_time_range"),
            sa.ForeignKeyConstraint(["booked_by_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"]),
            sa.ForeignKeyConstraint(["parent_booking_id"], ["room_bookings.id"]),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_room_bookings_id"), "room_bookings", ["id"], unique=False)

    # ── 17. enrollment_status_history ──────────────────────────────────────
    if not _table_exists("enrollment_status_history"):
        op.create_table(
            "enrollment_status_history",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("enrollment_id", sa.Integer(), nullable=False),
            sa.Column(
                "from_status",
                sa.Enum(
                    "pending", "confirmed", "awaiting_payment", "active",
                    "cancelled", "rejected", "withdrawn",
                    name="enrollmentstatus",
                    create_type=False,
                ),
                nullable=True,
            ),
            sa.Column(
                "to_status",
                sa.Enum(
                    "pending", "confirmed", "awaiting_payment", "active",
                    "cancelled", "rejected", "withdrawn",
                    name="enrollmentstatus",
                    create_type=False,
                ),
                nullable=False,
            ),
            sa.Column("changed_by", sa.Integer(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(
                ["enrollment_id"], ["enrollments.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_enrollment_status_history_id"),
            "enrollment_status_history",
            ["id"],
            unique=False,
        )


def downgrade() -> None:
    # Drop in reverse FK-dependency order
    if _table_exists("enrollment_status_history"):
        op.drop_index(
            op.f("ix_enrollment_status_history_id"),
            table_name="enrollment_status_history",
        )
        op.drop_table("enrollment_status_history")

    if _table_exists("room_bookings"):
        op.drop_index(op.f("ix_room_bookings_id"), table_name="room_bookings")
        op.drop_table("room_bookings")

    if _table_exists("report_cache"):
        op.drop_index("ix_report_cache_period", table_name="report_cache")
        op.drop_index("ix_report_cache_report_type", table_name="report_cache")
        op.drop_index(op.f("ix_report_cache_id"), table_name="report_cache")
        op.drop_table("report_cache")

    if _table_exists("notification_queue"):
        op.drop_index(op.f("ix_notification_queue_id"), table_name="notification_queue")
        op.drop_table("notification_queue")

    if _table_exists("tax_forms"):
        op.drop_index(op.f("ix_tax_forms_id"), table_name="tax_forms")
        op.drop_table("tax_forms")

    if _table_exists("feedback_forms"):
        op.drop_index(op.f("ix_feedback_forms_id"), table_name="feedback_forms")
        op.drop_table("feedback_forms")

    if _table_exists("testing_forms"):
        op.drop_index(op.f("ix_testing_forms_id"), table_name="testing_forms")
        op.drop_table("testing_forms")

    if _table_exists("teacher_forms"):
        op.drop_index(op.f("ix_teacher_forms_id"), table_name="teacher_forms")
        op.drop_table("teacher_forms")

    if _table_exists("preschool_forms"):
        op.drop_index(op.f("ix_preschool_forms_id"), table_name="preschool_forms")
        op.drop_table("preschool_forms")

    if _table_exists("adult_forms"):
        op.drop_index(op.f("ix_adult_forms_id"), table_name="adult_forms")
        op.drop_table("adult_forms")

    if _table_exists("child_forms"):
        op.drop_index(op.f("ix_child_forms_id"), table_name="child_forms")
        op.drop_table("child_forms")

    if _table_exists("audit_log"):
        op.drop_index("ix_audit_user_time", table_name="audit_log")
        op.drop_index("ix_audit_entity", table_name="audit_log")
        op.drop_index("ix_audit_log_created_at", table_name="audit_log")
        op.drop_index("ix_audit_log_entity_type", table_name="audit_log")
        op.drop_index("ix_audit_log_action", table_name="audit_log")
        op.drop_index("ix_audit_log_user_id", table_name="audit_log")
        op.drop_index(op.f("ix_audit_log_id"), table_name="audit_log")
        op.drop_table("audit_log")

    if _table_exists("documents"):
        op.drop_table("documents")

    if _table_exists("invoices"):
        op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
        op.drop_table("invoices")

    if _table_exists("student_groups"):
        op.drop_index(op.f("ix_student_groups_id"), table_name="student_groups")
        op.drop_table("student_groups")

    if _table_exists("classrooms"):
        op.drop_index(op.f("ix_classrooms_id"), table_name="classrooms")
        op.drop_table("classrooms")

    if _table_exists("teachers"):
        op.drop_index(op.f("ix_teachers_id"), table_name="teachers")
        op.drop_table("teachers")

    # Drop new enum types
    op.execute("DROP TYPE IF EXISTS bookingpurpose")
    op.execute("DROP TYPE IF EXISTS bookingstatus")
    op.execute("DROP TYPE IF EXISTS documentcategory")
