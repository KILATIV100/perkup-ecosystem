"""Leaderboard schemas"""

from datetime import date
from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    """Single leaderboard entry"""
    rank: int
    user_id: int
    username: str | None
    first_name: str | None
    photo_url: str | None
    total_score: int
    best_score: int
    games_played: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    period_type: str  # daily, weekly, monthly, all_time
    period_date: date
    game_id: int | None = None
    game_name: str | None = None
    entries: list[LeaderboardEntry]
    total_entries: int
    my_position: int | None = None
    my_entry: LeaderboardEntry | None = None
