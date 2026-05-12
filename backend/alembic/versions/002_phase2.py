"""phase 2 models

Revision ID: 002
Revises: 001
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel  # noqa: F401

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Add profile columns to user ---
    op.add_column('user', sa.Column('nickname', sa.String(), nullable=True, server_default=''))
    op.add_column('user', sa.Column('handle', sa.String(), nullable=True, server_default=''))
    op.add_column('user', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('user', sa.Column('job_title', sa.String(), nullable=True, server_default=''))
    op.add_column('user', sa.Column('career_level', sa.String(), nullable=True, server_default=''))
    op.add_column('user', sa.Column('company', sa.String(), nullable=True, server_default=''))
    op.add_column('user', sa.Column('bio', sa.String(), nullable=True, server_default=''))

    # --- Add new columns to course ---
    op.add_column('course', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('level', sa.String(), nullable=True, server_default=''))
    op.add_column('course', sa.Column('tags', sa.String(), nullable=True))
    op.add_column('course', sa.Column('rating_avg', sa.Float(), nullable=True, server_default='0'))
    op.add_column('course', sa.Column('review_count', sa.Integer(), nullable=True, server_default='0'))

    # --- Category ---
    op.create_table(
        'category',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('slug', sa.String(), nullable=False, unique=True),
        sa.Column('icon', sa.String(), server_default=''),
    )
    op.create_index('ix_category_slug', 'category', ['slug'])

    # --- MentorProfile ---
    op.create_table(
        'mentorprofile',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, unique=True),
        sa.Column('job_title', sa.String(), server_default=''),
        sa.Column('career_level', sa.String(), server_default=''),
        sa.Column('company', sa.String(), server_default=''),
        sa.Column('bio', sa.Text(), server_default=''),
        sa.Column('hourly_price', sa.Integer(), server_default='0'),
        sa.Column('session_minutes', sa.Integer(), server_default='60'),
        sa.Column('max_per_session', sa.Integer(), server_default='1'),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('rating_avg', sa.Float(), server_default='0'),
        sa.Column('review_count', sa.Integer(), server_default='0'),
        sa.Column('mentee_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- MentoringRequest ---
    op.create_table(
        'mentoringrequest',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mentor_profile_id', sa.Integer(), sa.ForeignKey('mentorprofile.id'), nullable=False),
        sa.Column('mentee_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status', sa.String(), server_default='PENDING'),
        sa.Column('message', sa.Text(), server_default=''),
        sa.Column('price', sa.Integer(), server_default='0'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- MentoringReview ---
    op.create_table(
        'mentoringreview',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mentor_profile_id', sa.Integer(), sa.ForeignKey('mentorprofile.id'), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('rating', sa.Float(), server_default='5'),
        sa.Column('content', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- Clip ---
    op.create_table(
        'clip',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), server_default=''),
        sa.Column('category', sa.String(), server_default=''),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('like_count', sa.Integer(), server_default='0'),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('comment_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- ClipComment ---
    op.create_table(
        'clipcomment',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('clip_id', sa.Integer(), sa.ForeignKey('clip.id'), nullable=False),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- ClipLike ---
    op.create_table(
        'cliplike',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('clip_id', sa.Integer(), sa.ForeignKey('clip.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
    )

    # --- Follow ---
    op.create_table(
        'follow',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('follower_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('following_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_follow_follower_id', 'follow', ['follower_id'])
    op.create_index('ix_follow_following_id', 'follow', ['following_id'])

    # --- CourseReview ---
    op.create_table(
        'coursereview',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('course.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('rating', sa.Float(), server_default='5'),
        sa.Column('content', sa.Text(), server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_coursereview_course_id', 'coursereview', ['course_id'])

    # --- Roadmap ---
    op.create_table(
        'roadmap',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), server_default=''),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('is_published', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # --- RoadmapStep ---
    op.create_table(
        'roadmapstep',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('roadmap_id', sa.Integer(), sa.ForeignKey('roadmap.id'), nullable=False),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('course.id'), nullable=False),
        sa.Column('step_order', sa.Integer(), server_default='0'),
        sa.Column('description', sa.String(), server_default=''),
    )

    # --- FK for course.category_id ---
    op.create_foreign_key('fk_course_category', 'course', 'category', ['category_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_course_category', 'course', type_='foreignkey')
    op.drop_table('roadmapstep')
    op.drop_table('roadmap')
    op.drop_table('coursereview')
    op.drop_table('follow')
    op.drop_table('cliplike')
    op.drop_table('clipcomment')
    op.drop_table('clip')
    op.drop_table('mentoringreview')
    op.drop_table('mentoringrequest')
    op.drop_table('mentorprofile')
    op.drop_table('category')
    op.drop_column('course', 'review_count')
    op.drop_column('course', 'rating_avg')
    op.drop_column('course', 'tags')
    op.drop_column('course', 'level')
    op.drop_column('course', 'category_id')
    op.drop_column('user', 'bio')
    op.drop_column('user', 'company')
    op.drop_column('user', 'career_level')
    op.drop_column('user', 'job_title')
    op.drop_column('user', 'avatar_url')
    op.drop_column('user', 'handle')
    op.drop_column('user', 'nickname')
