"""Game schemas"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class GameResponse(BaseModel):
    """Game response schema"""
    id: int
    name: str
    slug: str
    description: str | None = None
    max_points_per_game: int
    icon_url: str | None = None
    cover_image: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class GameListResponse(BaseModel):
    """List of games response"""
    games: list[GameResponse]


class GameSessionCreate(BaseModel):
    """Schema for starting a game session"""
    platform: str = "tma"


class GameSessionEnd(BaseModel):
    """Schema for ending a game session"""
    score: int
    duration_seconds: int


class GameSessionResponse(BaseModel):
    """Game session response schema"""
    id: UUID
    game_id: int
    game_name: str
    score: int
    duration_seconds: int | None = None
    points_earned: int
    experience_earned: int
    is_completed: bool
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class GameSessionStartResponse(BaseModel):
    """Response when starting a game session"""
    session_id: UUID
    game: GameResponse


class GameSessionEndResponse(BaseModel):
    """Response when ending a game session"""
    session: GameSessionResponse
    points_earned: int
    leaderboard_position: dict
