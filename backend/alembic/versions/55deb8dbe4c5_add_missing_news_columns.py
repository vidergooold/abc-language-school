"""add_missing_news_columns

Revision ID: 55deb8dbe4c5
Revises: e5ef08f40654
Create Date: 2026-04-11 19:25:35.463796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '55deb8dbe4c5'
down_revision: Union[str, Sequence[str], None] = 'e5ef08f40654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Сначала удаляем FK из lessons на rooms, потом саму таблицу ---
    op.drop_constraint('lessons_room_id_fkey', 'lessons', type_='foreignkey')

    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    op.drop_table('reviews')
    op.drop_index(op.f('ix_materials_id'), table_name='materials')
    op.drop_table('materials')
    op.drop_index(op.f('ix_revenue_analytics_id'), table_name='revenue_analytics')
    op.drop_table('revenue_analytics')
    op.drop_index(op.f('ix_expenses_id'), table_name='expenses')
    op.drop_table('expenses')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')

    # --- attendance ---
    op.add_column('attendance', sa.Column('student_group_id', sa.Integer(), nullable=False))
    op.add_column('attendance', sa.Column('teacher_id', sa.Integer(), nullable=True))
    op.add_column('attendance', sa.Column('status', sa.Enum('present', 'absent', 'late', 'excused', name='attendancestatus'), nullable=False))
    op.add_column('attendance', sa.Column('note', sa.Text(), nullable=True))
    op.add_column('attendance', sa.Column('lesson_date', sa.DateTime(), nullable=False))
    op.drop_constraint(op.f('attendance_student_id_fkey'), 'attendance', type_='foreignkey')
    op.create_foreign_key(None, 'attendance', 'teachers', ['teacher_id'], ['id'])
    op.create_foreign_key(None, 'attendance', 'student_groups', ['student_group_id'], ['id'])
    op.drop_column('attendance', 'late_minutes')
    op.drop_column('attendance', 'present')
    op.drop_column('attendance', 'notes')
    op.drop_column('attendance', 'student_id')

    # --- courses ---
    op.add_column('courses', sa.Column('category', sa.Enum('children', 'school', 'adults', 'corporate', 'exam_prep', name='coursecategory'), nullable=False))
    op.add_column('courses', sa.Column('duration_months', sa.Integer(), nullable=True))
    op.add_column('courses', sa.Column('lessons_per_week', sa.Integer(), nullable=True))
    op.add_column('courses', sa.Column('price_per_month', sa.Integer(), nullable=False))
    op.drop_column('courses', 'duration_weeks')
    op.drop_column('courses', 'price')

    # --- enrollments ---
    op.add_column('enrollments', sa.Column('name', sa.String(length=255), nullable=False))
    op.add_column('enrollments', sa.Column('phone', sa.String(length=50), nullable=False))
    op.add_column('enrollments', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('enrollments', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('enrollments', sa.Column('desired_course_id', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('student_type', sa.String(length=50), nullable=True))
    op.add_column('enrollments', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('source', sa.String(length=100), nullable=True))
    op.add_column('enrollments', sa.Column('status', sa.Enum('pending', 'confirmed', 'awaiting_payment', 'active', 'cancelled', 'rejected', 'withdrawn', name='enrollmentstatus'), nullable=False))
    op.add_column('enrollments', sa.Column('assigned_at', sa.DateTime(), nullable=True))
    op.add_column('enrollments', sa.Column('assigned_by', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('student_group_id', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('invoice_id', sa.Integer(), nullable=True))
    op.add_column('enrollments', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('enrollments', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('enrollments', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_enrollments_status'), 'enrollments', ['status'], unique=False)
    op.drop_constraint(op.f('enrollments_student_id_fkey'), 'enrollments', type_='foreignkey')
    op.drop_constraint(op.f('enrollments_payment_id_fkey'), 'enrollments', type_='foreignkey')
    op.drop_constraint(op.f('enrollments_course_id_fkey'), 'enrollments', type_='foreignkey')
    op.create_foreign_key(None, 'enrollments', 'invoices', ['invoice_id'], ['id'])
    op.create_foreign_key(None, 'enrollments', 'users', ['assigned_by'], ['id'])
    op.create_foreign_key(None, 'enrollments', 'courses', ['desired_course_id'], ['id'])
    op.create_foreign_key(None, 'enrollments', 'student_groups', ['student_group_id'], ['id'])
    op.create_foreign_key(None, 'enrollments', 'users', ['user_id'], ['id'])
    op.drop_column('enrollments', 'is_active')
    op.drop_column('enrollments', 'course_id')
    op.drop_column('enrollments', 'student_id')
    op.drop_column('enrollments', 'enrollment_date')
    op.drop_column('enrollments', 'completion_date')
    op.drop_column('enrollments', 'payment_id')

    # --- groups ---
    op.add_column('groups', sa.Column('status', sa.Enum('recruiting', 'active', 'finished', 'suspended', name='groupstatus'), nullable=False))
    op.alter_column('groups', 'start_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               nullable=True)
    op.alter_column('groups', 'end_date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)
    op.drop_column('groups', 'is_active')
    op.drop_column('groups', 'current_students')
    op.drop_column('groups', 'max_students')

    # --- lessons (FK на rooms уже удалён в самом начале) ---
    op.add_column('lessons', sa.Column('classroom_id', sa.Integer(), nullable=False))
    op.add_column('lessons', sa.Column('day_of_week', sa.Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', name='dayofweek'), nullable=False))
    op.add_column('lessons', sa.Column('time_start', sa.Time(), nullable=False))
    op.add_column('lessons', sa.Column('time_end', sa.Time(), nullable=False))
    op.add_column('lessons', sa.Column('lesson_date', sa.DateTime(), nullable=True))
    op.add_column('lessons', sa.Column('is_recurring', sa.Boolean(), nullable=True))
    op.add_column('lessons', sa.Column('created_by', sa.Integer(), nullable=True))
    op.alter_column('lessons', 'status',
               existing_type=postgresql.ENUM('scheduled', 'completed', 'cancelled', 'rescheduled', name='lessonstatus'),
               nullable=False)
    op.drop_constraint(op.f('lessons_teacher_id_fkey'), 'lessons', type_='foreignkey')
    # lessons_room_id_fkey уже удалён выше
    op.create_foreign_key(None, 'lessons', 'teachers', ['teacher_id'], ['id'])
    op.create_foreign_key(None, 'lessons', 'users', ['created_by'], ['id'])
    op.create_foreign_key(None, 'lessons', 'classrooms', ['classroom_id'], ['id'])
    op.drop_column('lessons', 'end_time')
    op.drop_column('lessons', 'date')
    op.drop_column('lessons', 'notes')
    op.drop_column('lessons', 'start_time')
    op.drop_column('lessons', 'room_id')

    # --- news ---
    op.add_column('news', sa.Column('slug', sa.String(length=300), nullable=True))
    op.add_column('news', sa.Column('tag', sa.String(length=100), nullable=True))
    op.add_column('news', sa.Column('body', sa.Text(), nullable=False))
    op.add_column('news', sa.Column('date', sa.String(length=20), nullable=True))
    op.add_column('news', sa.Column('is_pinned', sa.Boolean(), nullable=True))
    op.add_column('news', sa.Column('publish_at', sa.DateTime(), nullable=True))
    op.add_column('news', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('news', sa.Column('views_count', sa.Integer(), nullable=True))
    op.add_column('news', sa.Column('likes_count', sa.Integer(), nullable=True))
    op.alter_column('news', 'status',
               existing_type=postgresql.ENUM('draft', 'published', 'archived', name='newsstatus'),
               nullable=False)
    op.alter_column('news', 'author_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_index(op.f('ix_news_slug'), 'news', ['slug'], unique=True)
    op.create_index(op.f('ix_news_status'), 'news', ['status'], unique=False)
    op.create_foreign_key(None, 'news', 'news_categories', ['category_id'], ['id'])
    op.drop_column('news', 'content')
    op.drop_column('news', 'views')

    # --- notifications ---
    op.add_column('notifications', sa.Column('body', sa.Text(), nullable=False))
    op.add_column('notifications', sa.Column('channel', sa.Enum('email', 'sms', 'telegram', 'internal', name='notificationchannel'), nullable=False))
    op.add_column('notifications', sa.Column('recipient_email', sa.String(length=255), nullable=True))
    op.add_column('notifications', sa.Column('recipient_phone', sa.String(length=50), nullable=True))
    op.add_column('notifications', sa.Column('recipient_name', sa.String(length=255), nullable=True))
    op.add_column('notifications', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('notifications', sa.Column('created_by', sa.Integer(), nullable=True))
    op.alter_column('notifications', 'notification_type',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('schedule_reminder', 'payment_reminder', 'enrollment_confirm', 'news_published', 'custom', name='notificationtype'),
               nullable=False)
    op.alter_column('notifications', 'scheduled_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('notifications', 'status',
               existing_type=postgresql.ENUM('pending', 'sent', 'failed', name='notificationstatus'),
               nullable=False)
    op.drop_constraint(op.f('notifications_user_id_fkey'), 'notifications', type_='foreignkey')
    op.create_foreign_key(None, 'notifications', 'users', ['created_by'], ['id'])
    op.drop_column('notifications', 'message')
    op.drop_column('notifications', 'user_id')

    # --- payments ---
    op.add_column('payments', sa.Column('invoice_id', sa.Integer(), nullable=True))
    op.add_column('payments', sa.Column('student_group_id', sa.Integer(), nullable=True))
    op.add_column('payments', sa.Column('student_name', sa.String(length=255), nullable=False))
    op.add_column('payments', sa.Column('method', sa.Enum('cash', 'card', 'transfer', 'online', name='paymentmethod'), nullable=False))
    op.add_column('payments', sa.Column('paid_at', sa.DateTime(), nullable=True))
    op.add_column('payments', sa.Column('received_by', sa.Integer(), nullable=True))
    op.add_column('payments', sa.Column('comment', sa.Text(), nullable=True))
    op.alter_column('payments', 'amount',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)
    op.drop_constraint(op.f('payments_transaction_id_key'), 'payments', type_='unique')
    op.drop_constraint(op.f('payments_user_id_fkey'), 'payments', type_='foreignkey')
    op.create_foreign_key(None, 'payments', 'student_groups', ['student_group_id'], ['id'])
    op.create_foreign_key(None, 'payments', 'invoices', ['invoice_id'], ['id'])
    op.create_foreign_key(None, 'payments', 'users', ['received_by'], ['id'])
    op.drop_column('payments', 'status')
    op.drop_column('payments', 'payment_method')
    op.drop_column('payments', 'completed_at')
    op.drop_column('payments', 'currency')
    op.drop_column('payments', 'transaction_id')
    op.drop_column('payments', 'description')
    op.drop_column('payments', 'user_id')

    # --- users ---
    op.alter_column('users', 'full_name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('student', 'teacher', 'admin', 'manager', name='userrole'),
               nullable=False)
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'updated_at')

    # --- waitlist ---
    op.add_column('waitlist', sa.Column('group_id', sa.Integer(), nullable=True))
    op.add_column('waitlist', sa.Column('student_name', sa.String(length=255), nullable=False))
    op.add_column('waitlist', sa.Column('student_phone', sa.String(length=50), nullable=True))
    op.add_column('waitlist', sa.Column('student_email', sa.String(length=255), nullable=True))
    op.add_column('waitlist', sa.Column('student_type', sa.String(length=50), nullable=False))
    op.add_column('waitlist', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('waitlist', sa.Column('status', sa.Enum('waiting', 'notified', 'enrolled', 'cancelled', name='waitliststatus'), nullable=False))
    op.add_column('waitlist', sa.Column('notified_at', sa.DateTime(), nullable=True))
    op.add_column('waitlist', sa.Column('enrolled_at', sa.DateTime(), nullable=True))
    op.add_column('waitlist', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('waitlist', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.alter_column('waitlist', 'position',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint(op.f('waitlist_student_id_fkey'), 'waitlist', type_='foreignkey')
    op.create_foreign_key(None, 'waitlist', 'groups', ['group_id'], ['id'])
    op.drop_column('waitlist', 'student_id')
    op.drop_column('waitlist', 'added_at')
    op.drop_column('waitlist', 'notified')


def downgrade() -> None:
    op.add_column('waitlist', sa.Column('notified', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('waitlist', sa.Column('added_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('waitlist', sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'waitlist', type_='foreignkey')
    op.create_foreign_key(op.f('waitlist_student_id_fkey'), 'waitlist', 'users', ['student_id'], ['id'])
    op.alter_column('waitlist', 'position',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('waitlist', 'updated_at')
    op.drop_column('waitlist', 'created_at')
    op.drop_column('waitlist', 'enrolled_at')
    op.drop_column('waitlist', 'notified_at')
    op.drop_column('waitlist', 'status')
    op.drop_column('waitlist', 'comment')
    op.drop_column('waitlist', 'student_type')
    op.drop_column('waitlist', 'student_email')
    op.drop_column('waitlist', 'student_phone')
    op.drop_column('waitlist', 'student_name')
    op.drop_column('waitlist', 'group_id')
    op.add_column('users', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'role',
               existing_type=postgresql.ENUM('student', 'teacher', 'admin', 'manager', name='userrole'),
               nullable=True)
    op.alter_column('users', 'full_name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.add_column('payments', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('payments', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('currency', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('completed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('payment_method', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('status', postgresql.ENUM('pending', 'completed', 'failed', 'refunded', name='paymentstatus'), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'payments', type_='foreignkey')
    op.drop_constraint(None, 'payments', type_='foreignkey')
    op.drop_constraint(None, 'payments', type_='foreignkey')
    op.create_foreign_key(op.f('payments_user_id_fkey'), 'payments', 'users', ['user_id'], ['id'])
    op.create_unique_constraint(op.f('payments_transaction_id_key'), 'payments', ['transaction_id'], postgresql_nulls_not_distinct=False)
    op.alter_column('payments', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    op.drop_column('payments', 'comment')
    op.drop_column('payments', 'received_by')
    op.drop_column('payments', 'paid_at')
    op.drop_column('payments', 'method')
    op.drop_column('payments', 'student_name')
    op.drop_column('payments', 'student_group_id')
    op.drop_column('payments', 'invoice_id')
    op.add_column('notifications', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('notifications', sa.Column('message', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'notifications', type_='foreignkey')
    op.create_foreign_key(op.f('notifications_user_id_fkey'), 'notifications', 'users', ['user_id'], ['id'])
    op.alter_column('notifications', 'status',
               existing_type=postgresql.ENUM('pending', 'sent', 'failed', name='notificationstatus'),
               nullable=True)
    op.alter_column('notifications', 'scheduled_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('notifications', 'notification_type',
               existing_type=sa.Enum('schedule_reminder', 'payment_reminder', 'enrollment_confirm', 'news_published', 'custom', name='notificationtype'),
               type_=sa.VARCHAR(),
               nullable=True)
    op.drop_column('notifications', 'created_by')
    op.drop_column('notifications', 'error_message')
    op.drop_column('notifications', 'recipient_name')
    op.drop_column('notifications', 'recipient_phone')
    op.drop_column('notifications', 'recipient_email')
    op.drop_column('notifications', 'channel')
    op.drop_column('notifications', 'body')
    op.add_column('news', sa.Column('views', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('news', sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'news', type_='foreignkey')
    op.drop_index(op.f('ix_news_status'), table_name='news')
    op.drop_index(op.f('ix_news_slug'), table_name='news')
    op.alter_column('news', 'author_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('news', 'status',
               existing_type=postgresql.ENUM('draft', 'published', 'archived', name='newsstatus'),
               nullable=True)
    op.drop_column('news', 'likes_count')
    op.drop_column('news', 'views_count')
    op.drop_column('news', 'category_id')
    op.drop_column('news', 'publish_at')
    op.drop_column('news', 'is_pinned')
    op.drop_column('news', 'date')
    op.drop_column('news', 'body')
    op.drop_column('news', 'tag')
    op.drop_column('news', 'slug')
    op.add_column('lessons', sa.Column('room_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('lessons', sa.Column('start_time', postgresql.TIME(), autoincrement=False, nullable=False))
    op.add_column('lessons', sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('lessons', sa.Column('date', sa.DATE(), autoincrement=False, nullable=False))
    op.add_column('lessons', sa.Column('end_time', postgresql.TIME(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'lessons', type_='foreignkey')
    op.drop_constraint(None, 'lessons', type_='foreignkey')
    op.drop_constraint(None, 'lessons', type_='foreignkey')
    op.create_foreign_key(op.f('lessons_room_id_fkey'), 'lessons', 'rooms', ['room_id'], ['id'])
    op.create_foreign_key(op.f('lessons_teacher_id_fkey'), 'lessons', 'users', ['teacher_id'], ['id'])
    op.alter_column('lessons', 'status',
               existing_type=postgresql.ENUM('scheduled', 'completed', 'cancelled', 'rescheduled', name='lessonstatus'),
               nullable=True)
    op.drop_column('lessons', 'created_by')
    op.drop_column('lessons', 'is_recurring')
    op.drop_column('lessons', 'lesson_date')
    op.drop_column('lessons', 'time_end')
    op.drop_column('lessons', 'time_start')
    op.drop_column('lessons', 'day_of_week')
    op.drop_column('lessons', 'classroom_id')
    op.add_column('groups', sa.Column('max_students', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('groups', sa.Column('current_students', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('groups', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.alter_column('groups', 'end_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)
    op.alter_column('groups', 'start_date',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               nullable=False)
    op.drop_column('groups', 'status')
    op.add_column('enrollments', sa.Column('payment_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('enrollments', sa.Column('completion_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('enrollments', sa.Column('enrollment_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('enrollments', sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('enrollments', sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('enrollments', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'enrollments', type_='foreignkey')
    op.drop_constraint(None, 'enrollments', type_='foreignkey')
    op.drop_constraint(None, 'enrollments', type_='foreignkey')
    op.drop_constraint(None, 'enrollments', type_='foreignkey')
    op.drop_constraint(None, 'enrollments', type_='foreignkey')
    op.create_foreign_key(op.f('enrollments_course_id_fkey'), 'enrollments', 'courses', ['course_id'], ['id'])
    op.create_foreign_key(op.f('enrollments_payment_id_fkey'), 'enrollments', 'payments', ['payment_id'], ['id'])
    op.create_foreign_key(op.f('enrollments_student_id_fkey'), 'enrollments', 'users', ['student_id'], ['id'])
    op.drop_index(op.f('ix_enrollments_status'), table_name='enrollments')
    op.drop_column('enrollments', 'updated_at')
    op.drop_column('enrollments', 'created_at')
    op.drop_column('enrollments', 'rejection_reason')
    op.drop_column('enrollments', 'invoice_id')
    op.drop_column('enrollments', 'student_group_id')
    op.drop_column('enrollments', 'user_id')
    op.drop_column('enrollments', 'assigned_by')
    op.drop_column('enrollments', 'assigned_at')
    op.drop_column('enrollments', 'status')
    op.drop_column('enrollments', 'source')
    op.drop_column('enrollments', 'age')
    op.drop_column('enrollments', 'student_type')
    op.drop_column('enrollments', 'desired_course_id')
    op.drop_column('enrollments', 'comment')
    op.drop_column('enrollments', 'email')
    op.drop_column('enrollments', 'phone')
    op.drop_column('enrollments', 'name')
    op.add_column('courses', sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('courses', sa.Column('duration_weeks', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('courses', 'price_per_month')
    op.drop_column('courses', 'lessons_per_week')
    op.drop_column('courses', 'duration_months')
    op.drop_column('courses', 'category')
    op.add_column('attendance', sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('attendance', sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('attendance', sa.Column('present', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('attendance', sa.Column('late_minutes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'attendance', type_='foreignkey')
    op.drop_constraint(None, 'attendance', type_='foreignkey')
    op.create_foreign_key(op.f('attendance_student_id_fkey'), 'attendance', 'users', ['student_id'], ['id'])
    op.drop_column('attendance', 'lesson_date')
    op.drop_column('attendance', 'note')
    op.drop_column('attendance', 'status')
    op.drop_column('attendance', 'teacher_id')
    op.drop_column('attendance', 'student_group_id')
    op.create_table('rooms',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('capacity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('equipment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_available', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('rooms_pkey')),
    sa.UniqueConstraint('name', name=op.f('rooms_name_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_table('expenses',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('currency', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('expenses_pkey'))
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)
    op.create_table('revenue_analytics',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('period_start', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('period_end', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('total_revenue', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('total_expenses', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('net_profit', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('student_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('course_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('average_revenue_per_student', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('revenue_analytics_pkey'))
    )
    op.create_index(op.f('ix_revenue_analytics_id'), 'revenue_analytics', ['id'], unique=False)
    op.create_table('materials',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('file_url', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('file_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('uploaded_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('materials_course_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('materials_pkey'))
    )
    op.create_index(op.f('ix_materials_id'), 'materials', ['id'], unique=False)
    op.create_table('reviews',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('student_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('course_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_published', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name=op.f('reviews_course_id_fkey')),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('reviews_student_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('reviews_pkey'))
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)