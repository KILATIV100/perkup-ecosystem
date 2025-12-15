"""Leaderboard endpoints"""

from fastapi import APIRouter, Query
from typing import Literal

from app.api.deps import DbSession, OptionalUser
from app.schemas.leaderboard import LeaderboardResponse
from app.services.leaderboard_service import LeaderboardService

router = APIRouter()


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    db: DbSession,
    current_user: OptionalUser,
    period: Literal["daily", "weekly", "monthly", "all_time"] = "weekly",
    game_id: int | None = None,
    limit: int = Query(default=100, le=100)
):
    """
    Get leaderboard with optional filters.

    If authenticated, includes user's position in the leaderboard.
    """
    leaderboard_service = LeaderboardService(db)

    user_id = current_user.id if current_user else None

    return await leaderboard_service.get_leaderboard(
        period_type=period,
        game_id=game_id,
        limit=limit,
        user_id=user_id
    )
