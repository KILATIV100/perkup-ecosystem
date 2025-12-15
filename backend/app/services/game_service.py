"""Game service - business logic for game operations"""

from datetime import datetime, date
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game, GameSession
from app.models.user import User
from app.models.leaderboard import Leaderboard
from app.core.security import validate_game_score


class GameError(Exception):
    """Custom exception for game errors"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class GameService:
    """Service for game operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_games(self, active_only: bool = True) -> list[Game]:
        """Get all available games"""
        query = select(Game)
        if active_only:
            query = query.where(Game.is_active == True)
        result = await self.db.execute(query.order_by(Game.id))
        return list(result.scalars().all())

    async def get_game_by_slug(self, slug: str) -> Game | None:
        """Get game by slug"""
        result = await self.db.execute(select(Game).where(Game.slug == slug))
        return result.scalar_one_or_none()

    async def get_game_by_id(self, game_id: int) -> Game | None:
        """Get game by ID"""
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        return result.scalar_one_or_none()

    async def get_session_by_id(self, session_id: UUID) -> GameSession | None:
        """Get game session by ID"""
        result = await self.db.execute(
            select(GameSession).where(GameSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def start_session(self, user: User, game: Game, platform: str = "tma") -> GameSession:
        """Start a new game session"""
        session = GameSession(
            user_id=user.id,
            game_id=game.id,
            platform=platform,
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def end_session(
        self,
        session: GameSession,
        user: User,
        score: int,
        duration_seconds: int
    ) -> tuple[GameSession, int, dict]:
        """
        End a game session and calculate rewards.

        Returns:
            Tuple of (session, points_earned, leaderboard_positions)
        """
        game = await self.get_game_by_id(session.game_id)

        # Validate score (anti-cheat)
        if not validate_game_score(score, duration_seconds, game.slug):
            raise GameError("invalid_score", "Score validation failed")

        # Calculate points earned
        raw_points = int(score * float(game.points_conversion_rate))
        points_earned = min(raw_points, game.max_points_per_game)

        # Apply level bonus
        bonus = user.get_level_bonus()
        actual_points = int(points_earned * (1 + bonus))

        # Calculate experience (1 XP per 10 game points)
        experience_earned = score // 10

        # Update session
        session.score = score
        session.duration_seconds = duration_seconds
        session.points_earned = actual_points
        session.experience_earned = experience_earned
        session.is_completed = True
        session.completed_at = datetime.utcnow()

        # Update user stats
        user.points += actual_points
        user.experience += experience_earned
        user.total_games_played += 1
        if score > user.best_game_score:
            user.best_game_score = score

        # Check level up
        new_level = user.calculate_level()
        if new_level > user.level:
            user.level = new_level

        # Update leaderboard
        await self._update_leaderboard(user.id, game.id, score)

        await self.db.flush()

        # Get leaderboard positions
        positions = await self._get_user_positions(user.id, game.id)

        return session, actual_points, positions

    async def _update_leaderboard(self, user_id: int, game_id: int, score: int):
        """Update leaderboard entries for user"""
        today = date.today()

        # Update/create entries for each period type
        for period_type in ["daily", "weekly", "monthly", "all_time"]:
            if period_type == "daily":
                period_date = today
            elif period_type == "weekly":
                period_date = today - datetime.timedelta(days=today.weekday())
            elif period_type == "monthly":
                period_date = today.replace(day=1)
            else:
                period_date = date(2000, 1, 1)  # Fixed date for all_time

            # Try to get existing entry
            result = await self.db.execute(
                select(Leaderboard).where(
                    Leaderboard.user_id == user_id,
                    Leaderboard.game_id == game_id,
                    Leaderboard.period_type == period_type,
                    Leaderboard.period_date == period_date
                )
            )
            entry = result.scalar_one_or_none()

            if entry:
                entry.total_score += score
                entry.games_played += 1
                if score > entry.best_score:
                    entry.best_score = score
            else:
                entry = Leaderboard(
                    user_id=user_id,
                    game_id=game_id,
                    period_type=period_type,
                    period_date=period_date,
                    total_score=score,
                    best_score=score,
                    games_played=1,
                )
                self.db.add(entry)

    async def _get_user_positions(self, user_id: int, game_id: int) -> dict:
        """Get user's leaderboard positions"""
        positions = {}
        today = date.today()

        for period_type in ["daily", "weekly", "all_time"]:
            if period_type == "daily":
                period_date = today
            elif period_type == "weekly":
                period_date = today - datetime.timedelta(days=today.weekday())
            else:
                period_date = date(2000, 1, 1)

            # Count users with higher score
            result = await self.db.execute(
                select(func.count(Leaderboard.id) + 1)
                .where(
                    Leaderboard.game_id == game_id,
                    Leaderboard.period_type == period_type,
                    Leaderboard.period_date == period_date,
                    Leaderboard.total_score > (
                        select(Leaderboard.total_score)
                        .where(
                            Leaderboard.user_id == user_id,
                            Leaderboard.game_id == game_id,
                            Leaderboard.period_type == period_type,
                            Leaderboard.period_date == period_date
                        )
                        .scalar_subquery()
                    )
                )
            )
            position = result.scalar()
            positions[period_type] = position or 1

        return positions
