"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False, default=0),
        sa.Column('experience', sa.Integer(), nullable=False, default=0),
        sa.Column('level', sa.Integer(), nullable=False, default=1),
        sa.Column('total_checkins', sa.Integer(), nullable=False, default=0),
        sa.Column('total_games_played', sa.Integer(), nullable=False, default=0),
        sa.Column('best_game_score', sa.Integer(), nullable=False, default=0),
        sa.Column('language_code', sa.String(10), nullable=False, default='uk'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('referral_code', sa.String(20), nullable=True),
        sa.Column('referred_by_id', sa.BigInteger(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.UniqueConstraint('referral_code'),
    )
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'])
    op.create_index('idx_users_points', 'users', ['points'])

    # Locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False, default='Бровари'),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=False),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=False),
        sa.Column('checkin_radius_meters', sa.Integer(), nullable=False, default=100),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('working_hours', postgresql.JSONB(), nullable=True),
        sa.Column('features', postgresql.JSONB(), nullable=True),
        sa.Column('cover_image', sa.Text(), nullable=True),
        sa.Column('photos', postgresql.JSONB(), nullable=True),
        sa.Column('total_checkins', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # Checkins table
    op.create_table(
        'checkins',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('user_latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('user_longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('distance_meters', sa.Integer(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, default=1),
        sa.Column('experience_earned', sa.Integer(), nullable=False, default=10),
        sa.Column('checkin_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'location_id', 'checkin_date', name='uq_user_location_date'),
    )
    op.create_index('idx_checkins_user_date', 'checkins', ['user_id', 'checkin_date'])
    op.create_index('idx_checkins_location', 'checkins', ['location_id'])

    # Games table
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_points_per_game', sa.Integer(), nullable=False, default=20),
        sa.Column('points_conversion_rate', sa.Numeric(5, 2), nullable=False, default=0.02),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('cover_image', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # Game sessions table
    op.create_table(
        'game_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, default=0),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_earned', sa.Integer(), nullable=False, default=0),
        sa.Column('platform', sa.String(20), nullable=False, default='tma'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['game_id'], ['games.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_game_sessions_user', 'game_sessions', ['user_id'])
    op.create_index('idx_game_sessions_score', 'game_sessions', ['score'])

    # Events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=False),
        sa.Column('requirements', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('rewards', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('current_participants', sa.Integer(), nullable=False, default=0),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('cover_image', sa.Text(), nullable=True),
        sa.Column('images', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('idx_events_status_dates', 'events', ['status', 'starts_at', 'ends_at'])

    # Event participants table
    op.create_table(
        'event_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('progress', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('status', sa.String(20), nullable=False, default='registered'),
        sa.Column('rewards_claimed', sa.Boolean(), nullable=False, default=False),
        sa.Column('rewards_claimed_at', sa.DateTime(), nullable=True),
        sa.Column('registered_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_event_user'),
    )

    # Leaderboard table
    op.create_table(
        'leaderboard',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=True),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_date', sa.Date(), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=False, default=0),
        sa.Column('best_score', sa.Integer(), nullable=False, default=0),
        sa.Column('games_played', sa.Integer(), nullable=False, default=0),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['game_id'], ['games.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'game_id', 'period_type', 'period_date', name='uq_leaderboard_entry'),
    )
    op.create_index('idx_leaderboard_period_rank', 'leaderboard', ['period_type', 'period_date', 'rank'])

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('requirements', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('points_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('experience_reward', sa.Integer(), nullable=False, default=0),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('badge_color', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, default=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # User achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('progress', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, default=0),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )

    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=True),
        sa.Column('action_data', postgresql.JSONB(), nullable=True),
        sa.Column('channel', sa.String(20), nullable=False, default='telegram'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('leaderboard')
    op.drop_table('event_participants')
    op.drop_table('events')
    op.drop_table('game_sessions')
    op.drop_table('games')
    op.drop_table('checkins')
    op.drop_table('locations')
    op.drop_table('users')
