"""Pydantic schemas for API validation"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfileResponse,
)
from app.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationListResponse,
)
from app.schemas.checkin import (
    CheckinCreate,
    CheckinResponse,
    CheckinHistoryResponse,
)
from app.schemas.game import (
    GameResponse,
    GameSessionCreate,
    GameSessionEnd,
    GameSessionResponse,
)
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventListResponse,
    EventParticipantResponse,
)
from app.schemas.leaderboard import (
    LeaderboardEntry,
    LeaderboardResponse,
)
from app.schemas.auth import (
    TelegramAuthRequest,
    TokenResponse,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfileResponse",
    "LocationCreate",
    "LocationResponse",
    "LocationListResponse",
    "CheckinCreate",
    "CheckinResponse",
    "CheckinHistoryResponse",
    "GameResponse",
    "GameSessionCreate",
    "GameSessionEnd",
    "GameSessionResponse",
    "EventCreate",
    "EventResponse",
    "EventListResponse",
    "EventParticipantResponse",
    "LeaderboardEntry",
    "LeaderboardResponse",
    "TelegramAuthRequest",
    "TokenResponse",
]
