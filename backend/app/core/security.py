"""Security utilities for authentication and authorization"""

import hmac
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import parse_qs

from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings


class TokenData(BaseModel):
    """JWT token payload data"""
    user_id: int
    telegram_id: int
    exp: datetime


def validate_telegram_init_data(init_data: str) -> dict:
    """
    Validate initData from Telegram Web App
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("Telegram bot token not configured")

    parsed = parse_qs(init_data)
    hash_value = parsed.get('hash', [''])[0]

    if not hash_value:
        raise ValueError("Hash not found in init data")

    # Create data_check_string
    check_items = []
    for key, value in sorted(parsed.items()):
        if key != 'hash':
            check_items.append(f"{key}={value[0]}")
    data_check_string = '\n'.join(check_items)

    # Create secret_key
    secret_key = hmac.new(
        "WebAppData".encode(),
        settings.TELEGRAM_BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    # Verify hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if calculated_hash != hash_value:
        raise ValueError("Invalid hash")

    # Check auth_date (not older than 24 hours)
    auth_date = int(parsed.get('auth_date', ['0'])[0])
    if time.time() - auth_date > 86400:
        raise ValueError("Data is too old")

    # Parse user data
    user_data = json.loads(parsed.get('user', ['{}'])[0])
    return user_data


def create_access_token(user_id: int, telegram_id: int) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)
    payload = {
        "user_id": user_id,
        "telegram_id": telegram_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT access token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenData(
            user_id=payload.get("user_id"),
            telegram_id=payload.get("telegram_id"),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError:
        return None


def validate_game_score(score: int, duration: int, game_slug: str) -> bool:
    """
    Basic validation of game results to prevent cheating
    """
    # Maximum possible score per second (depends on game)
    max_score_per_second = {
        'coffee-jump': 10,
        'coffee-match': 5,
        'barista-rush': 3,
        'coffee-quiz': 2,
        'spin-wheel': 100,
    }

    max_possible = duration * max_score_per_second.get(game_slug, 5)

    # Allow 20% tolerance
    if score > max_possible * 1.2:
        return False

    # Minimum game duration
    if duration < 5:
        return False

    return True
