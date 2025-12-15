"""Seed initial data - locations, games, achievements

Revision ID: 002
Revises: 001
Create Date: 2025-01-15

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Seed locations
    op.execute("""
        INSERT INTO locations (name, slug, address, city, latitude, longitude, checkin_radius_meters, description, working_hours, features, is_active, created_at)
        VALUES
        ('Mark Mall', 'mark-mall', 'Київська, 239, Бровари', 'Бровари', 50.514794, 30.782308, 100,
         'Затишна кав''ярня в торговому центрі Mark Mall. Ідеальне місце для перерви під час шопінгу.',
         '{"mon-fri": "09:00-21:00", "sat-sun": "10:00-21:00"}',
         '["wifi", "parking", "outdoor_seating"]',
         true, NOW()),
        ('Парк Приозерний', 'park-priozerny', 'вул. Фіалковського, 27а, Бровари', 'Бровари', 50.501265, 30.754011, 100,
         'Кав''ярня з видом на парк. Ідеальне місце для прогулянок з кавою.',
         '{"mon-sun": "08:00-21:00"}',
         '["wifi", "terrace", "park_view", "pet_friendly"]',
         true, NOW())
    """)

    # Seed games
    op.execute("""
        INSERT INTO games (name, slug, description, max_points_per_game, points_conversion_rate, is_active, created_at)
        VALUES
        ('Coffee Jump', 'coffee-jump', 'Стрибай якомога вище та збирай кавові зерна! Класичний endless jumper з кавовою тематикою.', 20, 0.02, true, NOW()),
        ('Coffee Match', 'coffee-match', 'Класичний Match-3 з кавовою тематикою. З''єднуй три та більше однакових елементів!', 15, 0.01, true, NOW()),
        ('Barista Rush', 'barista-rush', 'Готуй каву для клієнтів на швидкість! Не дай черзі вийти з-під контролю.', 25, 0.04, true, NOW()),
        ('Coffee Quiz', 'coffee-quiz', 'Перевір свої знання про каву! 10 питань, 15 секунд на відповідь.', 20, 0.1, true, NOW()),
        ('Колесо Фортуни', 'spin-wheel', 'Крути колесо та вигравай призи! Одне безкоштовне обертання на день.', 100, 0.01, true, NOW())
    """)

    # Seed achievements
    op.execute("""
        INSERT INTO achievements (slug, name, description, category, requirements, points_reward, experience_reward, is_active, sort_order, created_at)
        VALUES
        -- Checkin achievements
        ('first-checkin', 'Перший крок', 'Зроби свій перший check-in', 'checkin', '{"type": "checkins", "count": 1}', 10, 20, true, 1, NOW()),
        ('regular-visitor', 'Завсідник', 'Зроби 10 check-ins', 'checkin', '{"type": "checkins", "count": 10}', 25, 50, true, 2, NOW()),
        ('coffee-fan', 'Фанат кави', 'Зроби 50 check-ins', 'checkin', '{"type": "checkins", "count": 50}', 50, 100, true, 3, NOW()),
        ('legend', 'Легенда', 'Зроби 100 check-ins', 'checkin', '{"type": "checkins", "count": 100}', 100, 200, true, 4, NOW()),
        ('explorer', 'Дослідник', 'Зроби check-in в обох локаціях', 'checkin', '{"type": "locations", "count": 2}', 30, 50, true, 5, NOW()),

        -- Game achievements
        ('first-game', 'Гравець', 'Зіграй свою першу гру', 'game', '{"type": "games", "count": 1}', 5, 10, true, 10, NOW()),
        ('gamer', 'Геймер', 'Зіграй 50 ігор', 'game', '{"type": "games", "count": 50}', 25, 50, true, 11, NOW()),
        ('pro-gamer', 'Pro Gamer', 'Зіграй 200 ігор', 'game', '{"type": "games", "count": 200}', 50, 100, true, 12, NOW()),
        ('high-score', 'High Score', 'Потрап в топ-10 таблиці лідерів', 'game', '{"type": "leaderboard", "position": 10}', 50, 100, true, 13, NOW()),
        ('champion', 'Чемпіон', 'Виграй турнір', 'game', '{"type": "tournament", "win": true}', 100, 200, true, 14, NOW()),

        -- Social achievements
        ('promoter', 'Промоутер', 'Запроси 1 друга', 'social', '{"type": "referrals", "count": 1}', 20, 30, true, 20, NOW()),
        ('influencer', 'Інфлюенсер', 'Запроси 5 друзів', 'social', '{"type": "referrals", "count": 5}', 50, 100, true, 21, NOW()),
        ('ambassador', 'Амбасадор', 'Запроси 20 друзів', 'social', '{"type": "referrals", "count": 20}', 200, 300, true, 22, NOW()),

        -- Streak achievements
        ('week-streak', 'Тиждень з нами', 'Check-in 7 днів поспіль', 'streak', '{"type": "streak", "days": 7}', 30, 50, true, 30, NOW()),
        ('month-streak', 'Місяць з нами', 'Check-in 30 днів поспіль', 'streak', '{"type": "streak", "days": 30}', 100, 200, true, 31, NOW()),
        ('unbreakable', 'Незламний', 'Check-in 100 днів поспіль', 'streak', '{"type": "streak", "days": 100}', 300, 500, true, 32, NOW())
    """)


def downgrade() -> None:
    op.execute("DELETE FROM achievements")
    op.execute("DELETE FROM games")
    op.execute("DELETE FROM locations")
