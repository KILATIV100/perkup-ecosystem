# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.utils.telegram import validate_telegram_init_data
from app.utils.jwt import create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Inline schema (тимчасово)
class TelegramAuthRequest(BaseModel):
    init_data: str

@router.post("/telegram")
async def telegram_auth(
    data: TelegramAuthRequest,
    db: Session = Depends(get_db)
):
    """Авторізація через Telegram Mini App"""
    
    # Валідуємо init_data
    user_data = validate_telegram_init_data(
        data.init_data,
        settings.TELEGRAM_BOT_TOKEN
    )
    
    if not user_data:
        raise HTTPException(
            status_code=401, 
            detail="Invalid Telegram authentication data"
        )
    
    telegram_id = user_data.get('id')
    
    # Шукаємо або створюємо користувача
    user = db.query(models.User).filter(
        models.User.telegram_id == telegram_id
    ).first()
    
    if not user:
        user = models.User(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            photo_url=user_data.get('photo_url'),
            language_code=user_data.get('language_code', 'uk')
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.username = user_data.get('username')
        user.first_name = user_data.get('first_name')
        user.last_name = user_data.get('last_name')
        user.photo_url = user_data.get('photo_url')
        user.last_active_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    
    # Створюємо JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "telegram_id": telegram_id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_DAYS * 86400,
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "photo_url": user.photo_url,
            "points": user.points,
            "level": user.level,
            "total_checkins": user.total_checkins,
            "best_game_score": user.best_game_score,
            "created_at": user.created_at.isoformat()
        }
    }