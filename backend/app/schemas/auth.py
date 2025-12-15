"""Authentication schemas"""

from pydantic import BaseModel


class TelegramAuthRequest(BaseModel):
    """Request for Telegram authentication"""
    init_data: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TelegramLoginWidget(BaseModel):
    """Telegram Login Widget data"""
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: int
    hash: str
