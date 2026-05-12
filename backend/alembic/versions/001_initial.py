"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # User
    op.create_table(
        'user',
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False, server_default=''),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_user_email', 'user', ['email'])

    # Course
    op.create_table(
        'course',
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instructor_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Module
    op.create_table(
        'module',
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['course.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Lesson
    op.create_table(
        'lesson',
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False, server_default='video'),
        sa.Column('video_source_type', sa.String(), nullable=True),
        sa.Column('content_url', sa.String(), nullable=True),
        sa.Column('text_content', sa.String(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['module_id'], ['module.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Enrollment
    op.create_table(
        'enrollment',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['course_id'], ['course.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Payment
    op.create_table(
        'payment',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('payment_key', sa.String(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['course_id'], ['course.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
    )
    op.create_index('ix_payment_order_id', 'payment', ['order_id'])


def downgrade() -> None:
    op.drop_table('payment')
    op.drop_table('enrollment')
    op.drop_table('lesson')
    op.drop_table('module')
    op.drop_table('course')
    op.drop_index('ix_user_email', 'user')
    op.drop_table('user')
