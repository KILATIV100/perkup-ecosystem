"""Leaderboard service - business logic for leaderboard operations"""

from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.leaderboard import Leaderboard
from app.models.user import User
from app.models.game import Game
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse


class LeaderboardService:
    """Service for leaderboard operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_period_date(self, period_type: str) -> date:
        """Get the period date based on period type"""
        today = date.today()
        if period_type == "daily":
            return today
        elif period_type == "weekly":
            return today - timedelta(days=today.weekday())
        elif period_type == "monthly":
            return today.replace(day=1)
        else:  # all_time
            return date(2000, 1, 1)

    async def get_leaderboard(
        self,
        period_type: str = "weekly",
        game_id: int | None = None,
        limit: int = 100,
        user_id: int | None = None
    ) -> LeaderboardResponse:
        """Get leaderboard for a specific period and game"""
        period_date = self._get_period_date(period_type)

        # Build query
        query = (
            select(Leaderboard, User)
            .join(User, Leaderboard.user_id == User.id)
            .where(
                Leaderboard.period_type == period_type,
                Leaderboard.period_date == period_date
            )
        )

        if game_id:
            query = query.where(Leaderboard.game_id == game_id)
        else:
            query = query.where(Leaderboard.game_id.is_(None))

        query = query.order_by(Leaderboard.total_score.desc()).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        # Build entries
        entries = []
        for rank, (leaderboard, user) in enumerate(rows, 1):
            entry = LeaderboardEntry(
                rank=rank,
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                photo_url=user.photo_url,
                total_score=leaderboard.total_score,
                best_score=leaderboard.best_score,
                games_played=leaderboard.games_played,
            )
            entries.append(entry)

        # Get game name if game_id provided
        game_name = None
        if game_id:
            game_result = await self.db.execute(
                select(Game.name).where(Game.id == game_id)
            )
            game_name = game_result.scalar_one_or_none()

        # Find user's position if provided
        my_position = None
        my_entry = None
        if user_id:
            my_position, my_entry = await self._get_user_position(
                user_id, period_type, period_date, game_id
            )

        return LeaderboardResponse(
            period_type=period_type,
            period_date=period_date,
            game_id=game_id,
            game_name=game_name,
            entries=entries,
            total_entries=len(entries),
            my_position=my_position,
            my_entry=my_entry,
        )

    async def _get_user_position(
        self,
        user_id: int,
        period_type: str,
        period_date: date,
        game_id: int | None
    ) -> tuple[int | None, LeaderboardEntry | None]:
        """Get user's position in leaderboard"""
        # Get user's entry
        query = select(Leaderboard).where(
            Leaderboard.user_id == user_id,
            Leaderboard.period_type == period_type,
            Leaderboard.period_date == period_date
        )
        if game_id:
            query = query.where(Leaderboard.game_id == game_id)
        else:
            query = query.where(Leaderboard.game_id.is_(None))

        result = await self.db.execute(query)
        user_entry = result.scalar_one_or_none()

        if not user_entry:
            return None, None

        # Count users with higher score
        count_query = select(func.count(Leaderboard.id)).where(
            Leaderboard.period_type == period_type,
            Leaderboard.period_date == period_date,
            Leaderboard.total_score > user_entry.total_score
        )
        if game_id:
            count_query = count_query.where(Leaderboard.game_id == game_id)
        else:
            count_query = count_query.where(Leaderboard.game_id.is_(None))

        count_result = await self.db.execute(count_query)
        position = count_result.scalar() + 1

        # Get user info
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        entry = LeaderboardEntry(
            rank=position,
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            photo_url=user.photo_url,
            total_score=user_entry.total_score,
            best_score=user_entry.best_score,
            games_played=user_entry.games_played,
        )

        return position, entry

    async def get_user_stats(self, user_id: int) -> dict:
        """Get user's leaderboard statistics"""
        stats = {}

        for period_type in ["daily", "weekly", "monthly", "all_time"]:
            period_date = self._get_period_date(period_type)

            # Get user's total score across all games
            result = await self.db.execute(
                select(func.sum(Leaderboard.total_score))
                .where(
                    Leaderboard.user_id == user_id,
                    Leaderboard.period_type == period_type,
                    Leaderboard.period_date == period_date
                )
            )
            total_score = result.scalar() or 0

            stats[period_type] = {
                "total_score": total_score,
                "period_date": period_date.isoformat()
            }

        return stats
